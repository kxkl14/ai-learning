import pandas as pd
import numpy as np

print("--- 第一课：缺省值处理 ---")
# 创建一个带有缺失值（NaN）的表格
data = {
    "姓名": ["张三", "李四", "王五", "赵六"],
    "成绩": [85, np.nan, 76, np.nan],            # np.nan 代表空值
    "城市": ["北京", "上海", "北京", "深圳"]
}
df = pd.DataFrame(data)
print("原始表格：")
print(df)

# 1. 检查缺失值（isnull 返回布尔值， sum 统计每列空了多少个）
print("\n每列缺失值的数量: ")
print(df.isnull().sum())

# 2. 删除缺失值（dropna 会删除包含空值的行）
print("\n删除缺失值后的表格: ")
print(df.dropna)

# 3. 填充缺失值（fillna 用指定值填补空值）
print("\n用0填补缺失值: ")
print(df.fillna(0))

print("\n--- 第二课: 分组聚合 ---")
# 用刚才的数据，去掉空值来练手
df_clean = df.dropna()
# 如果删完只剩一行没法分组，我们手补一份完整数据
data_full = {
    "姓名": ["张三", "李四", "王五", "赵六"],
    "成绩": [85, 92, 76, 59],
    "城市": ["北京", "上海", "北京", "深圳"]
}
df_full = pd.DataFrame(data_full)

# 按“城市”分组，计算“成绩”的平均分
grouped = df_full.groupby("城市")["成绩"].mean()
print("各城市的平均成绩：")
print(grouped)

# 如果想看各个城市有多少人，最高分是多少
print("\n各个城市的成绩统计: ")
print(df_full.groupby("城市")["成绩"].agg(["count", "mean", "max"]))

print("\n--- 第三课：多表合并 (Merge) ---")
# 表1：学生的成绩
df_students = pd.DataFrame({
    "姓名": ["张三", "李四", "王五"],
    "城市": ["北京", "上海", "北京"],
    "成绩": [85, 92, 76]
})

# 表2：城市的省份信息
df_cities = pd.DataFrame({
    "城市": ["北京", "上海", "广州"],
    "省份": ["北京市", "上海市", "广东省"]
})

# 按“城市”这一列，把两张表合并起来（类似 VLOOKUP）
merged = pd.merge(df_students, df_cities, on="城市", how="left")
print("合并后的表格（左连接）：")
print(merged)

