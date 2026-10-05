# 第一课：列表（list）
print("--- 列表操作 ---")
# 创建列表（可以放字符串，也可以放数字）
fruits = ["苹果","香蕉","橘子","草莓"]

# 1. 查：通过索引获取元素（索引从0开始！）
print("第一个水果：",fruits[0])              # 苹果
print("最后一个水果：",fruits[-1])           # 草莓(-1表示倒数第一个)

# 2. 改：直接修改某个位置的值
fruits[1] = "葡萄"
print("修改后的列表：",fruits)

# 3. 增：在末尾追加一个
fruits.append("西瓜")
print("追加后的列表：",fruits)

# 4. 删：删除一个元素
fruits.remove("橘子")
print("删除后的列表：",fruits)

# 5. 查长度：一共有多少个元素
print("水果总数：",len(fruits))

# 第二课：字典（Dictionary）
print("\n--- 字典操作 ---")
# 创建一个学生字典
student = {
    "name": "gaole",
    "age": 25,
    "city": "北京",
    "is_learning": True,
}

# 1. 取值：用中括号加键名
print("学生姓名：", student["name"])

# 2. 改值：直接赋值
student["age"] = 26
print("修改后的年龄：", student["age"])

# 3. 增加：给一个新键赋值
student['job'] = "AI学习者"
print("增加职业后的字典：", student)

# 4. 获取所有的键和值
print("所有的键：", student.keys())
print("所有的值：",student.values())

# 第三课：实战 - 学生通讯录
print("\n--- 学生通讯录 ---")
contacts = [
    {"name": "gaole", "phone": "13800000001", "city": "北京"},
    {"name": "张三", "phone": "13800000002", "city": "上海"},
    {"name": "李四", "phone": "13800000003", "city": "广州"}
]

for person in contacts:
    print(f"姓名: {person['name']}, 电话：{person['phone']}, 城市：{person['city']}")
    