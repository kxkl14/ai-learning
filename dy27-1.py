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

# ==================== 1. 初始化数据库（持久化记忆） ===================
DB_NAME = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCRMENT,
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

# ================== 2. 初始化客户端 ================
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
    if city == "北京": return "北京今天晴，25度。"
    return f"{city}的天气数据暂未收录。"

def get_current_time():
    return datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate_math(expression):
    try: return f"计算结果是: {eval(expression)}"
    except: return "计算错误"

tools = [
    {"type": "function", "function": {"name": "get_weather", "description": "获取指定城市的当前天气", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "获取当前的日期和时间", "parameters":{"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculate_math", "description": "计算数学表达式", "parameters": {"type": "object", "properties":{"expression": {"type": "string"}}, "required": ["expression"]}}}                                                                                                                                                   
]

def chat_once(messages):
    return client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools,
        extra_body={"thinking": {"type": "disabled"}}
    )

# ================== 4. 页面 UI 与侧边栏 =================
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

# ================== 5. 主聊天逻辑 ==================
# 从数据库加载历史
if "messages" not in st.session_state:
    st.session_state.messgaes = load_messages()
    
# 渲染历史记录
for msg in st.session_state.messages:
    if msg.get("role") in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 用户输入
