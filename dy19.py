import streamlit  as st
from openai import OpenAI

# =====================================================
# 1. 页面基础设置
# =====================================================
st.set_page_config(page_title="我的 AI 助手", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 助手")
st.caption("基于 DeepSeek 和 Streamlit 构建")

# =====================================================
# 2. 初始化客户端和记忆
# =====================================================
# 请在下面填入你的DeepSeek API key
client = OpenAI(
    api_key="sk-你的 deepseek api pay",
    base_url="https://api.deepseek.com"
)

# Streamlit 每次交互都会重新运行代码，所以需要用 session_state 来保护聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个幽默风趣的 AI 助手，请用简短的话语回答问题。"}
    ]
# 强制把之前的错误缓存清空
if len(st.session_state.messages) > 0 and "content" not in st.session_state.messages[0]:
    st.session_state.messages = [{"role": "system", "content": "你是一个幽默风趣的 AI 助手。"}]

# =======================================================
# 3. 渲染历史聊天记录
# =======================================================
# 遍历历史记录（通过 system 设定），显示在页面上
for msg in st.session_state.messages:
    # 使用 .get（） 方法，如果没有对应的键就返回 Nome，不会报错
    role = msg.get("role")
    content = msg.get("content")


    if role != "system" and content:
        with st.chat_message(role):
            st.markdown(str(content))

# =======================================================
# 4. 接受用户输入并生成回复
# =======================================================
# st.chat_input 会在页面底部生成一个输入框
if user_input := st.chat_input("发消息给我的 AI 助手..."):

    # 显示用户发的话
    with st.chat_message("user"):
        st.markdown(user_input)

    # 把用户的话加入记忆
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 显示 AI 的回复（包含流式打字机效果）
    with st.chat_message("assistant"):
        try:
            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-flash",
                messages=st.session_state.messages,
                stream=True
            )

            # 定义一个生成器，专门用来给前端吐字
            def generate_chunks():
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            # st.write_stream 会自动处理打字机效果，并还回完整文本
            ai_reply = st.write_stream(generate_chunks())

            # 把 AI 的回复也加入记忆
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            st.error(f"出错了: {e}")
