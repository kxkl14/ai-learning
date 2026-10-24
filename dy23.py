import json
from openai import OpenAI

# 1. 初始化客户端
client = OpenAI(
    api_key="sk-2b3715335a124216bb1c8b18bd468c3c",
    base_url="https://api.deepseek.com"
)

# 2. 定义本地工具函数
def get_weather(city):
    """模拟查询天气的函数"""
    if city == "北京":
        return "北京今天晴, 25度, 微风。"
    elif city == "上海":
        return "上海今天中雨, 22度, 记得带伞。"
    else:
        return f"{city}的天气数据暂未收录。"


# 3. 告诉大模型我们有哪些工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
# 4. 开启对话循环
print("🤖 Agent 已就绪！你可以问天气, 或者其他问题。")
while True:
    user_input = input("\n你: ")
    if user_input.lower() in ['退出', 'exit']:
        break

    # 维护对话历史
    messages = [{"role": "user", "content": user_input}]

    # 第一次请求：让大模型判断是否需要调用工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )

    response_message = response.choices[0].message

    # 检查大模型是否想要调用工具
    if response_message.tool_calls:
        print("🔎 [AI 决定调用工具...]")

        # 把 AI 要调用工具的请求加入历史记录
        messages.append(response_message)

        # 遍历 AI 决定调用的所以工具（可能一次调用多个）
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"👉 调用的函数: {function_name}")
            print(f"👉 传入的参数: {arguments}")

            # 在本地执行函数
            if function_name == "get_weather":
                function_result = get_weather(arguments["city"])
                print(f"👉 本地函数返回: {function_result}")

            # 把函数的执行结果加入历史记录
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_result
            })

        # 第二次请求：把工具结果发给大模型，让它总结回复
        second_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        print(f"\n🤖 AI 回答: {second_response.choices[0].message.content}")

    else:
        # 如果不需要调用工具，大模型会直接回答
        print(f"\n🤖 AI 回答: {response_message.content}")


