from openai import OpenAI

# 1. 初始化客户端（填入你的 deepseek Key）
client = OpenAI(
    api_key="sk-你的key",   # 替换成你的真实 Key
    base_url="https://api.deepseek.com"
)

# 2. 初始化聊天记录列表（包含一个系统人设）
messages = [
    {"role": "system", "content": "你是一个幽默风趣的 AI 助手，请用简短的话语回答问题。"}
]
print("🤖 AI 助手已上线！输入'退出' 或 'exit' 结束对话。" )
print("-" * 40)

# 3. 开启一个无限循环，保持对话
while True:
    # 接受用户输入
    user_input = input("\n你: ")

    # 退出条件
    if user_input.lower() in ['退出', 'exit', 'quit']:
        print("👋 再见！")
        break

    # 如果输入为空，跳过
    if not user_input.strip():
        continue

 
    # 4. 把用户的话加入历史记录
    messages.append({"role": "user", "content": user_input})


    try:
        # 5. 发送请求（注意这里我们加入完整的 messages 列表
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            stream=True     # 开启流式输出，体验更好
        )

        print("AI: ", end="", flush=True)
        full_reply = ""         # 用来拼接完整的 AI 回复

        # 6. 接受流式输出并打印
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    print(delta.content, end="", flush=True)
                    full_reply += delta.content     # 把每次蹦出的字拼接起来


        print()  # 换行

        # 7. 极其关键的一步：把 AI 的回答也加入历史记录！
        messages.append({"role": "assistant", "content": full_reply})

    except Exception as e:
        print(f"\n❌️ 出错了：{e}")
        # 如果出错了，把刚才用户的话从列表删除，防止历史记录错乱
        messages.pop()