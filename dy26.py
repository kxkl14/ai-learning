import streamlit as st
import json
import datetime
import sqlite3
from openai import OpenAI
import os

# ================= 1. 初始化数据库 =================
DB_NAME = "agent_memory.db"

def init_db():
    """创建或连接数据库，并建立消息表"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 表结构：id(自增), role(角色), content(内容), timestamp(时间)
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  role TEXT, 
                  content TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    return conn

def save_message(role, content):
    """将消息存入数据库"""
    if not content: return
    conn = init_db()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)", (role, content, now))
    conn.commit()
    conn.close()

def load_messages():
    """从数据库加载所有历史消息"""
    conn = init_db()
    c = conn.cursor()
    # 只取 role 和 content
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    # 转换成 OpenAI 需要的格式
    return [{"role": row[0], "content": row[1]} for row in rows]

# ================= 2. 页面与客户端初始化 =================
st.set_page_config(page_title="全栈 AI Agent (带记忆)", page_icon="🤖", layout="centered")
st.title("🤖 全栈多功能 AI Agent")
st.caption("具备本地持久化记忆功能")

api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=api_key,  # 👈 替换成你的 Key
    base_url="https://api.deepseek.com"
)

# ================= 3. 定义本地工具函数与 Tools =================
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

# ================= 4. 界面逻辑与状态保持 =================
with st.sidebar:
    if st.button("🧹 清空数据库记忆"):
        conn = init_db()
        conn.execute("DELETE FROM chat_history")
        conn.commit()
        conn.close()
        st.session_state.messages = []
        st.rerun()

# 核心改动：从数据库加载历史记录到 session_state
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# 渲染历史记录
for msg in st.session_state.messages:
    if msg.get("role") in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 接收用户输入
if user_input := st.chat_input("输入你的问题，比如：北京天气怎么样？"):
    
    # 1. 显示并保存用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)  # 👈 存入数据库
    
    # 2. 第一次请求
    with st.chat_message("assistant"):
        with st.spinner("🤔 AI 正在思考中..."):
            response_message = chat_once(st.session_state.messages).choices[0].message
        
        if response_message.tool_calls:
            st.session_state.messages.append(response_message.model_dump())
            # 注意：工具调用的记录不需要存进长时数据库，因为下次对话不会依赖具体的工具参数记录
            
            with st.status("🛠️ AI 正在调用本地工具...", expanded=True) as status:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    
                    st.write(f"👉 调用: `{function_name}`")
                    if function_name == "get_weather": result = get_weather(arguments.get("city", ""))
                    elif function_name == "get_current_time": result = get_current_time()
                    elif function_name == "calculate_math": result = calculate_math(arguments.get("expression", ""))
                    else: result = "未知工具"
                        
                    st.write(f"✅ 返回: {result}")
                    st.session_state.messages.append({
                        "role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": str(result)
                    })
                status.update(label="✅ 工具执行完毕", state="complete")
            
            # 3. 第二次请求：总结
            final_response = chat_once(st.session_state.messages).choices[0].message
            st.markdown(final_response.content)
            st.session_state.messages.append({"role": "assistant", "content": final_response.content})
            save_message("assistant", final_response.content)  # 👈 存入数据库
            
        else:
            st.markdown(response_message.content)
            st.session_state.messages.append({"role": "assistant", "content": response_message.content})
            save_message("assistant", response_message.content)  # 👈 存入数据库