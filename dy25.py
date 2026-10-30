import streamlit as st
import json
import datetime
from openai import OpenAI
import os

# ================= 1. 页面与客户端初始化 =================
st.set_page_config(page_title="全栈多功能 AI 代理", page_icon="🤖", layout="wide")
st.title("🤖 全栈多功能 AI 代理")
st.caption("基于 Streamlit 和 DeepSeek 构建，支持查天气、看时间、算数学")

# ⚠️ 请替换为你自己的 API Key（建议使用环境变量，防止泄露）
# 如果你不会配置环境变量，直接写在下面也行，但千万别发到网上了
API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# ================= 2. 定义本地工具函数 =================
def get_weather(city):
    if not city: return "请先告诉我城市名称。"
    if city == "北京": return "北京今天晴，25度，微风。"
    if city == "上海": return "上海今天小雨，20度，记得带伞。"
    return f"{city}的天气数据暂未收录。"

def get_current_time():
    return datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate_math(expression):
    try:
        # 注意：实际生产环境中慎用 eval，这里仅作演示
        return str(eval(expression))
    except Exception as e:
        return f"计算失败: {e}"

# ================= 3. 定义工具描述 (让大模型知道有哪些工具) =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，例如：北京"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的具体时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，例如：2+2*3"}
                },
                "required": ["expression"]
            }
        }
    }
]

# ================= 4. 初始化与渲染历史记录 =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史记录 (兼容字典和Pydantic对象)
for msg in st.session_state.messages:
    # 如果是字典，用 get 获取；如果是对象，用 getattr 获取
    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
    content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
    
    # 只渲染用户和助手的常规对话，工具调用的内部细节不展示在聊天框
    if role in ["user", "assistant"] and content:
        with st.chat_message(role):
            st.markdown(content)

# ================= 5. 接收用户输入并处理 =================
if user_input := st.chat_input("输入你的问题，比如：北京天气怎么样？"):
    
    # 1. 显示用户的话并存入记忆
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. 第一次请求：带上工具，判断是否要用
    with st.chat_message("assistant"):
        with st.spinner("🤔 AI 正在思考中..."):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            
            # 统一转成字典存入历史
            st.session_state.messages.append(response_message.model_dump())

            # 3. 如果大模型决定调用工具
            if response_message.tool_calls:
                with st.status("🛠️ AI 正在调用本地工具...", expanded=True) as status:
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        
                        # 解析参数 (就是之前报错的地方)
                        arguments_str = tool_call.function.arguments
                        try:
                            arguments = json.loads(arguments_str) if arguments_str else {}
                        except json.JSONDecodeError:
                            arguments = {}
                            
                        st.write(f"👍 调用函数：`{function_name}` | 参数：`{arguments}`")

                        # 执行对应的本地函数
                        if function_name == "get_weather":
                            result = get_weather(arguments.get("city", ""))
                        elif function_name == "get_current_time":
                            result = get_current_time()
                        elif function_name == "calculate_math":
                            result = calculate_math(arguments.get("expression", ""))
                        else:
                            result = "未知工具"

                        st.write(f"✅ 工具返回：{result}")

                        # 保存工具执行结果存入记忆
                        st.session_state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(result)
                        })
                    status.update(label="✅ 工具调用完成", state="complete")

                # 4. 第二次请求：拿到工具结果后，让 AI 生成最终回答
                with st.spinner("✍️ AI 正在整理最终回答..."):
                    second_response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=st.session_state.messages
                    )
                    final_message = second_response.choices[0].message
                    
                    # 显示最终回答并存入记忆
                    st.markdown(final_message.content)
                    st.session_state.messages.append(final_message.model_dump())
            else:
                # 如果不需要调用工具，直接显示大模型的原话
                st.markdown(response_message.content)