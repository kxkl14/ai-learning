import streamlit as st
import json
import datetime
import sqlite3
import httpx
import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 加载环境变量
load_dotenv()                    # 读取 .env 文件

# ================= 1. 初始化数据库 (持久化记忆) =================
DB_NAME = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  role TEXT, 
                  content TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    return conn

def save_message(role, content):
    if not content: return
    conn = init_db()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)", (role, content, now))
    conn.commit()
    conn.close()

def load_messages():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

# ================= 2. 初始化客户端 =================
client =OpenAI(
    # 👇 从环境变量中读取 key， 如果读取不到就报错提示
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    timeout=60.0,
    max_retries=3,
    http_client=httpx.Client(http2=False, transport=httpx.HTTPTransport(local_address="0.0.0.0"))
)

# ================= 3. 工具函数定义 =================
def get_weather(city):
    if not city: return "请先告诉我城市名称。"
    if city == "北京": return "北京今天晴, 25度。"
    return f"{city}的天气数据暂未收录。"

def get_current_time():
    return datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate_math(expression):
    try: return f"计算结果是: {eval(expression)}"
    except: return "计算错误"

tools = [
    {"type": "function", "function": {"name": "get_weather", "description": "获取指定城市的当前天气", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "获取当前的日期和时间", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculate_math", "description": "计算数学表达式", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}}
]

def chat_once(messages):
    return client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools,
        extra_body={"thinking": {"type": "disabled"}}
    )

# ================= 4. 页面 UI 与侧边栏 =================
st.set_page_config(page_title="全能 AI 助手", page_icon="🤖", layout="centered")
st.title("🤖 全能 AI 助手 (带记忆 + RAG)")
st.caption("支持工具调用、记忆保存、文档阅读")

# 初始化 RAG 变量
if "rag_vectorizer" not in st.session_state:
    st.session_state.rag_vectorizer = None
    st.session_state.rag_chunks = []

with st.sidebar:
    st.header("📂 知识库上传")
    uploaded_file = st.file_uploader("上传 TXT 文件让我阅读", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        chunks = [line.strip() for line in text.split('\n') if line.strip()]
        if chunks:
            vec = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
            st.session_state.rag_vectorizer = vec
            st.session_state.rag_chunks = chunks
            st.session_state.rag_vectors = vec.fit_transform(chunks)
            st.success(f"✅ 文档已加载！切分为 {len(chunks)} 个片段。")
    
    st.divider()
    if st.button("🧹 清空数据库记忆"):
        conn = init_db()
        conn.execute("DELETE FROM chat_history")
        conn.commit()
        conn.close()
        st.session_state.messages = []
        st.rerun()

# ================= 5. 主聊天逻辑 =================
# 从数据库加载历史
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# 渲染历史记录
for msg in st.session_state.messages:
    if msg.get("role") in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 用户输入
if user_input := st.chat_input("输入你的问题，比如：北京天气怎么样？"):
    
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)
    
    # --- 核心改动：RAG 检索 ---
    rag_context = ""
    if st.session_state.rag_vectorizer is not None:
        # 把问题转成向量，去找文档中最相关的片段
        q_vec = st.session_state.rag_vectorizer.transform([user_input])
        similarities = cosine_similarity(q_vec, st.session_state.rag_vectors)[0]
        best_chunk = st.session_state.rag_chunks[similarities.argmax()]
        if similarities.max() > 0.1:  # 相似度阈值
            rag_context = f"\n\n【参考文档内容】：\n{best_chunk}\n（请结合上述参考文档回答用户问题）"
            st.info(f"🔍 检索到文档片段：{best_chunk}")

    # 构造发给大模型的消息（加入 RAG 上下文）
    messages_for_ai = list(st.session_state.messages)
    if rag_context:
        messages_for_ai.insert(0, {"role": "system", "content": f"你是一个全能助手。{rag_context}"})

    with st.chat_message("assistant"):
        with st.spinner("🤔 AI 正在思考中..."):
            response_message = chat_once(messages_for_ai).choices[0].message
        
        if response_message.tool_calls:
            st.session_state.messages.append(response_message.model_dump())
            
            with st.status("🛠️ AI 正在调用本地工具...", expanded=True) as status:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments or "{}")
                    except:
                        arguments = {}
                    
                    st.write(f"👉 调用: `{function_name}`")
                    if "weather" in function_name:
                        result = get_weather(arguments.get("city", ""))
                    elif "time" in function_name:
                        result = get_current_time()
                    elif "calc" in function_name:
                        result = calculate_math(arguments.get("expression", ""))
                    else:
                        result = "未知工具"
                        
                    st.write(f"✅ 返回: {result}")
                    st.session_state.messages.append({
                        "role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": str(result)
                    })
                    # 工具调用记录不需要存入数据库，仅存于 session
                status.update(label="✅ 工具执行完毕", state="complete")
            
            # 第二次请求总结
            final_response = chat_once(st.session_state.messages).choices[0].message
            st.markdown(final_response.content)
            st.session_state.messages.append({"role": "assistant", "content": final_response.content})
            save_message("assistant", final_response.content)
            
        else:
            st.markdown(response_message.content)
            st.session_state.messages.append({"role": "assistant", "content": response_message.content})
            save_message("assistant", response_message.content)