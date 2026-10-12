# 1. 导入所需的工具包
from sklearn.datasets import load_iris             # 经典的鸢尾花数据集
from sklearn.model_selection import train_test_split     # 划分数据集的工具
from sklearn.neighbors import KNeighborsClassifier       # K近邻算法（一种简单的分类模型）
from sklearn.metrics import accuracy_score               # 计算准确率

print("--- 机器学习初体验 ---")

# 2. 加载数据
# x 是特征（花瓣长、花瓣宽等），y 是标签（是哪种花：0，1，2）
X, y = load_iris(return_X_y=True)
print(f"数据集大小: 共 {X.shape[0]} 条样本, 每条有 {X.shape[1]} 个特征。")

# 3. 划分数据集
# 80% 用来训练模型（训练集），20% 用来考试（测试集）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"训练集大小: {X_train.shape[0]} 条，测试集大小：{X_test.shape[0]} 条。")

print("\n--- 开始训练模型 ---")
# 4. 创建模型（K=3 表示参考最近的3个邻居）
model = KNeighborsClassifier(n_neighbors=3)

# 5. 训练模型（这就是“学习”的过程，把训练数据喂给模型）
model.fit(X_train, y_train)
print("模型训练完成！")

# 6. 用测试集进行预测
predictions = model.predict(X_test)

# 7. 对比预测结果和真实结果，计算准确率
accuracy = accuracy_score(y_test, predictions)
print(f"模型预测准确率: {accuracy * 100:.2f}%")

print("\n--- 实战：预测新数据 ---")
# 我们手工构建一个数据：[花萼长，花萼宽，花瓣长，花瓣宽]
# 比如：5.1，3.5，1.4，0.2（这通常属于第一种花）
new_flower = [[5.1, 3.5, 1.4, 0.2]]

# 让模型猜一猜
result = model.predict(new_flower)

# 把数字 0，1，2 转换成花的名字
flower_names = ['山鸢尾', '变色鸢尾', '维吉尼亚鸢尾']
print(f"这朵新花被预测为：{flower_names[result[0]]}")
