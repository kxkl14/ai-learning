import json
import datetime
from openai import OpenAI

# 1. 初始化客户端
client = OpenAI(
    api_key="你的Deepseek_API_KEY",  # 👈 替换成你的真实 Key
    base_url="https://api.deepseek.com"
)

# ================= 2. 定义本地工具函数 =================
def get_weather(city):
    """查天气"""
    if city == "北京": return "北京今天晴，25度。"
    return f"{city}的天气数据暂未收录。"

def get_current_time():
    """获取当前时间"""
    now = datetime.datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

def calculate_math(expression):
    """算数学题（注意：实际应用中直接用 eval 有安全风险，这里仅做演示）"""
    try:
        # 限制只允许数字和基本的运算符
        allowed_chars = set("0123456789+-*/(). ")
        if not set(expression).issubset(allowed_chars):
            return "包含非法字符，无法计算。"
        result = eval(expression)
        return f"计算结果是：{result}"
    except Exception as e:
        return f"计算出错：{e}"

# ================= 3. 告诉大模型我们有哪些工具 =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名称"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {"type": "object", "properties": {}} # 不需要参数
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "计算数学表达式的结果",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "数学表达式，如 '345 * 12'"}},
                "required": ["expression"]
            }
        }
    }
]

# 4. 开启对话循环
print("🤖 多功能 Agent 已就绪！你可以问天气、看时间或算数学题。")
while True:
    user_input = input("\n你: ")
    if user_input.lower() in ['退出', 'exit']:
        break

    messages = [{"role": "user", "content": user_input}]

    # 第一次请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    
    response_message = response.choices[0].message

    # 检查是否调用工具
    if response_message.tool_calls:
        print(f"🔍 [AI 决定调用 {len(response_message.tool_calls)} 个工具...]")
        messages.append(response_message)
        
        # 遍历所有被调用的工具（支持多工具并行）
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"👉 调用: {function_name} | 参数: {arguments}")

            # 执行对应函数
            if function_name == "get_weather":
                result = get_weather(arguments.get("city", ""))
            elif function_name == "get_current_time":
                result = get_current_time()
            elif function_name == "calculate_math":
                result = calculate_math(arguments.get("expression", ""))
            else:
                result = "未知工具"

            print(f"   返回: {result}")

            # 收集结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": result
            })

        # 第二次请求：让大模型总结
        second_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        print(f"\n🤖 AI 回答: {second_response.choices[0].message.content}")

    else:
        print(f"\n🤖 AI 回答: {response_message.content}")