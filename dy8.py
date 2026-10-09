import pandas as pd        # 惯例简写为 pd

print("--- 第一课：创建 DataFrame ---")

# 从字典创建一个简单的表格
data = {
    "姓名": ["张三", "李四", "王五", "赵六"],
    "年龄": [18, 20, 19, 22],
    "城市": ["北京", "上海", "广州", "深圳"]
}
df = pd.DataFrame(data)

print("打印整个表格：")
print(df)

# 查看前两行
print("\n查看前两行: ")
print(df.head(2))

# 查看表格形状 （行数，列数）
print("\n表格形状: ", df.shape)

# 为了防止文件丢失，我们先检查并生成一份示例成绩数据
import os
if not os.path.exists("scores.csv"):
    print("未找到 scores.csv, 正在重新生成...")
    with open("scores.csv", "w", encoding="utf-8") as f:
        f.write("姓名，成绩\n")
        f.write("张三, 85\n")
        f.write("李四, 92\n")
        f.write("王五, 76\n")
        f.write("赵六, 59\n")
        f.write("钱七, 88\n")

print("\n--- 第二课：读取 csv 文件 ---")
# 读取文件 （注意：pandas 读取 csv 文件最好有表头，比如“姓名，成绩”）
try:
    # 假设第一行是列名 （header=0）
    df_scores = pd.read_csv("scores.csv", names=["姓名","成绩"])
    print("读取成功！数据如下：")
    print(df_scores)
except Exception as e:
    print(f"读取失败: {e}")

print("\n--- 第三课：数据筛选与统计 ---")
if 'df_scores' in locals():
    # 1. 描述性统计 （均值、标准差等）
    print("成绩描述性统计：")
    print(df_scores["成绩"].describe())

    # 2. 筛选成绩大于80分的学生
    print("\n成绩大于80分的学生: ")
    high_scores = df_scores[df_scores["成绩"] > 80]
    print(high_scores)

    # 3. 按成绩降序排序
    print("\n按成绩降序排序: ")
    sorted_df = df_scores.sort_values(by="成绩", ascending=False)
    print(sorted_df)

    # 4. 计算及格率
    pass_count = len(df_scores[df_scores["成绩"] >= 60])
    total_count = len(df_scores)
    print(f"\n总人数: {total_count}, 及格人数: {pass_count}, 及格率: {pass_count/total_count*100:.1f}%")


