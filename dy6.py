# 第一课：文件写入
print("--- 文件写入 ---")

# “w” 表示写入模式（覆盖原文件），如果文件不存在会自动创建
# encoding="utf-8" 是为了防止中文乱码
with open("test_data.txt", "w", encoding="utf-8") as f:
    f.write("hello python!\n")
    f.write("这是我的第一行文件写入。\n")
    f.write("今天天气不错。\n")

print("写入完成！")

# 第二课：追加内容
print("\n--- 追加文件 ---")
# “a” 表示追加模式（在原文件末尾增加，不覆盖）
with open("test_data.txt", "a", encoding="utf-8") as f:
    f.write("这是追加的第二行。\n")

# 第三课：读取文件
print("\n--- 读取文件 ---")
with open("test_data.txt", "r", encoding="utf-8") as f:
    content = f.read()           # 一次性读取全部内容
    print("文件里的内容如下：")
    print(content)

# 第四课：错误处理
print("--- 错误处理 ---")

try:
    # 尝试执行这里的代码
    score = int(input("请输入你的成绩："))
    print(f"你输入的成绩是：{score}")
except ValueError:
    # 如果上面发生了 ValueError 错误（比如输入了字母），就执行到这里
    print("输入错误！请输入纯数字，不要输入文字或符号。")

print("程序继续运行，没有崩溃！")

# 第五课：实战 - 成绩记录器
print("\n--- 成绩记录器 ---")

def save_score(name, score):
    # 以追加模式存入 csv 文件（表格文件）
    with open("scores.scv", "a", encoding="utf-8") as f:
        f.write(f"{name},{score}\n")

# 循环录入3个学生的成绩
for i in range(3):
    print(f"\n录入第 {i+1} 个学生：")
    student_name = input("请输入学生姓名：")

    try:
        student_score = int(input("请输入成绩："))
        save_score(student_name, student_score)
        print(f"{student_name} 的成绩已保存！")
    except ValueError:
        print("成绩必须是数字！本次录入失败，跳过该学生。")

# 最后读取所有成绩
print("\n--- 所有录入的成绩 ---")
try:
    with open("scores.csv", "r", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("目前还没有任何成绩记录。")
    


