# 第一课：函数基础
print("--- 函数基础 ---")

# 1. 定义无参函数（不需要材料，就能干活）
def say_hello():
    print("大家好，我是一个AI学习助手！") 

# 调用函数（用名字加括号，就能执行上面的代码）
say_hello()
say_hello()                         # 可以反复调用，不用重新写

# 2. 定义带参数的函数（需要你提供材料）
def greet(name, city):
    print(f"你好，我是{name}, 来自{city}。")

greet("gaole", "北京")               # 传入参数
greet("张三", "上海")

# 第二课：返回值（return）
print("\n--- 返回值 ---")

def add(a, b):
    # 注意这里用的是 return，不是 print！
    return a + b

# 调用函数，接收返回值
result = add(3, 5)
print("3 + 5 的结果是:",result)

# 甚至可以嵌套使用
final_result = add(add(1, 2), 10)
print("1 +2 + 10 的结果是: ", final_result)

# 第三课：实战 - 成绩等级函数
print("\n--- 成绩等级判定 ---")

def get_grade(score):
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

# 用列表装几个成绩，用循环批量调用函数
scores = [95, 85, 59, 72]
for s in scores:
    # 调用函数，接收返回值
    grade = get_grade(s)
    print(f"分数 {s} 的等级是: {grade}")
    