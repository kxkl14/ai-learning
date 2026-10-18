from openai import OpenAI

# 1. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key="sk-feb1d87b94274b599dbaebe68058e358",  # 👈 替换为你的真实 Key
    base_url="https://api.deepseek.com"  # 官方推荐地址
)

print("🤖 DeepSeek 正在思考，准备输出：\n")

# 2. 发送请求
try:
    response = client.chat.completions.create(
        model="deepseek-flash",  # 官方当前主推的通用模型
        messages=[
            {"role": "system", "content": "你是一个资深的 Python 编程导师，回答要简洁幽默。"},
            {"role": "user", "content": "请用一句话解释什么是机器学习？"}
        ],
        stream=True,
        temperature=0.3
    )

    # 3. 流式接收并打印（打字机效果）
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            
    print("\n\n✅ 接收完毕！")

except Exception as e:
    print(f"发生错误啦：{e}")