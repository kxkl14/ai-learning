import matplotlib.pyplot as plt

# 1. 解决中文显示问题（windows 系统专用）
plt.rcParams['font.sans-serif'] = ['SimHei']      # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False        # 用来正常显示负号

print("--- 第一课：折线图 ---")
# 2. 准备数据
days = ["周一", "周二", "周三", "周四", "周五"]
study_hours = [2, 3, 2.5, 4, 3.5]

# 3. 画图
plt.figure(figsize=(8, 4))                        # 设置画布大小
plt.plot(days, study_hours, marker='o', color='blue', label='学习时长')

# 4. 添加标题和标签
plt.title("一周学习时长趋势", fontsize=16)
plt.xlabel("星期", fontsize=12)
plt.ylabel("小时", fontsize=12)
plt.legend()                                      # 显示图例
plt.grid(True)                                    # 显示网格

# 5. 保存图片（比 plt.show() 更靠谱，不会弹窗卡住）
plt.savefig("line_chart.png", dpi=150)
print("折线图已保存为 line_chart.png")
plt.close()                                       # 关闭当前画布

print("\n--- 第二课：柱状图 ---")
# 用 day 9 的数据
cities = ["北京", "上海", "深圳"]
avg_scores = [80.5, 92.0, 59.0]

plt.figure(figsize=(8, 4))
# 画柱状图
plt.bar(cities, avg_scores, color=['#FF9999', '#66B2FF', '#99FF99'])
plt.title("各城市平均成绩对比", fontsize=16)
plt.xlabel("城市", fontsize=12)
plt.ylabel("平均分", fontsize=12)

# 给柱子加上数字标签
for i, v in enumerate(avg_scores):
    plt.text(i, v + 1, str(v), ha='center', fontsize=12)

plt.savefig("bar_chart.png", dpi=150)
print("柱状图已保存为 bar_chart.png")
plt.close()

print("\n--- 第三课：直方图 ---")
# 生成一批成绩数据（模拟一个班）
import numpy as np
scores = np.random.normal(75, 10, 50)             # 均值75，标准差10， 生成50个成绩

plt.figure(figsize=(8, 4))
plt.hist(scores, bins=10, color='skyblue', edgecolor='black')     # bins=10 表示分成10组
plt.title("班级成绩分布直方图", fontsize=16)
plt.xlabel("分数", fontsize=12)
plt.ylabel("人数", fontsize=12)
plt.savefig("hist_chart.png")
plt.close()