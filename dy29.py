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

load_dotenv()

# ================== 1. 数据库（同昨天）=================
DB_NAME = "chat_history.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

def save_message(role, content):
    if not content: return
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)", (role, content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def load_messages():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

# ================= 2. 客户端 ================
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    api_key_val = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key_val,
    base_url="https://api.deepseek.com",
    timeout=60.0,
    max_retries=3,
    http_client=httpx.Client(http2=False, transport=httpx.HTTPTransport(local_address="0.0.0.0"))
)

# =================== 3. 工具 ===============
def get_weather(city):
    if city == "北京": return "北京今天晴，25度。"
    return f"{city}的天气信息暂未收录。"

def get_current_time():
    return datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate_math(expression):
    try: return f"计算结果: {eval(expression)}"
    except: return "计算错误"

tools = [
    {"type": "function", "function": {"name": "get_weather", "description": "获取指定城市的当前天气", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "获取当前的日期和时间", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculate_math", "description": "计算数学表达式", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}}
]

# =================== 4. UI 页面 ================
st.set_page_config(page_title="全能 AI 助手", page_icon="🤖", layout="centered")
st.title("🤖 全能 AI 助手 (流式输出版)")

if "rag_vectorizer" not in st.session_state:
    st.session_state.rag_vectorizer = None

with st.sidebar:
    st.header("📂 知识库上传")
    uploaded_file = st.file_uploader("上传 TXT 文件", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        chunks = [line.strip() for line in text.split("\n") if line.strip()]
        if chunks:
            vec = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
            st.session_state.rag_vectorizer = vec
            st.session_state.rag_chunks = chunks
            st.session_state.rag_vectors = vec.fit_transform(chunks)
            st.success(f"✅️ 文档已加载！（{len(chunks)} 段）")

    st.divider()
    if st.button("🧹 清空记忆"):
        conn = init_db()
        conn.execute("DELETE FROM chat_history")
        conn.commit()
        conn.close()
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

for msg in st.session_state.messages:
    if msg.get("role") in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# =================== 5. 核心交互逻辑 ================
if user_input := st.chat_input("请输入你的问题..."):

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)

    # RAG 检索
    rag_context = ""
    if st.session_state.rag_vectorizer is not None:
        q_vec = st.session_state.rag_vectorizer.transform([user_input])
        similarities = cosine_similarity(q_vec, st.session_state.rag_vectors)[0]
        best_chunk = st.session_state.rag_chunks[similarities.argmax()]
        if similarities.max() > 0.1:
            rag_context = f"\n\n【参考文档内容】: \n{best_chunk}\n (请结合参考文档回答)"
            st.info(f"🔍 检索到: {best_chunk}")

    # 安全的复制历史记录，并统一转换为字典格式
    messages_for_ai = []
    for msg in st.session_state.messages:
        if isinstance(msg, dict):
            messages_for_ai.append(msg)
        else:
            # 兼容 OpenAI 对象
            messages_for_ai.append(msg.model_dump())

    # 插入RAG 上下文（如果存在）
    if rag_context:
        messages_for_ai.insert(0, {"type": "system", "content": f"你是一个全能助手。{rag_context}"})

    # 【关键】过滤掉不完整的信息，确保 role 和 content 都存在
    clean_messages = []
    for m in messages_for_ai:
        # 必须是字典，必须有 role，必须有 content
        if isinstance(m, dict) and "role" in m and "content" in m and m["content"] is not None:
            # 兼容处理：如果是工具调用信息，DeepSeek 要求 content 不能是空字符串（除非有 tool_calls）
            if m["content"] == "" and "tool_calls" not in m:
                continue
            clean_messages.append(m)

    messages_for_ai = clean_messages

    # 第一次请求（判断工具，这里不需要流式）
    with st.spinner("AI 思考中..."):
        response = client.chat.completions.create(
            model="deepseek-flash", messages=messages_for_ai, tools=tools, 
            extra_body={"thinking": {"type": "disabled"}}
        )
        response_message = response.choices[0].message

    if response_message.tool_calls:
        st.session_state.messages.append(response_message.model_dump())

        with st.status("🛠️ 正在执行工具...", expanded=True) as status:
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")
                st.write(f"调用: '{func_name}'")

                if "weather" in func_name: res = get_weather(args.get("city", ""))
                elif "time" in func_name: res = get_current_time()
                elif "calc" in func_name: res = calculate_math(args.get("expression", ""))
                else: res = f"未知工具"

                st.write(f"结果: {res}")
                st.session_state.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": str(res)})
            status.update(label="✅️ 执行完毕", state="complete", expanded=False)

            # 第二次请求（带工具结果， 并且开启流式！）
            stream_res = client.chat.completions.create(
                model="deepseek-flash", messages=st.session_state.messages, stream=True,
                extra_body={"thinking": {"type": "disabled"}}
            )

            with st.chat_message("assistant"):
                #  核心魔法：st.write_stream 自动处理流式输出和渲染
                final_content = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream_res if chunk.choices)

            st.session_state.messages.append({"role": "assistant", "content": final_content})
            save_message("assistant", final_content)

    else:
        # 没有调用工具，直接开启流式对话
        stream_res = client.chat.completions.create(
            model="deepseek-flash", messages=messages_for_ai, stream=True,
            extra_body={"thinking": {"type": "disabled"}}
        )
        with st.chat_message("assistant"):
            final_content = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream_res if chunk.choices)

        st.session_state.messages.append({"role": "assistant", "content": final_content})
        save_message("assistant", final_content)