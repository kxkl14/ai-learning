import pandas as pd
import seaborn as sns
import numpy as np

print("--- 第一步：加载泰坦尼克号数据集 ---")
# 加载数据（如果报错提示没有 seaborn，请在终端运行 pip install seaborn）
df = sns.load_dataset('titanic')

# 看看数据长什么样，有哪些列
print(df.head())
print("\n数据基本信息: ")
print(df.info())

print("\n--- 第二步：数据清洗 ---")

# 1. 丢掉缺失值太多的列，或者不需要的列
df =df.drop(columns=['deck', 'embark_town', 'alive', 'who', 'adult_male', 'class'])
print("精简后的列: ", df.columns.tolist())

# 2. 处理缺失值：年龄用中位数，登船港口用众数
df['age'] = df['age'].fillna(df['age'].median())
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
df = df.dropna()

# 3. 把文字转换成数字（机器只认识数字！）
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
# 登船港口用独热编码（One-Hot）转换
df = pd.get_dummies(df, columns=['embarked'], drop_first=True)

print("清洗完成！当前数据维度: ", df.shape)

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

print("\n--- 第三步：训练决策树模型 ---")
# 准备特征和标签
X = df.drop('survived', axis=1)
y = df['survived']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建决策树模型（max_depth=3 防止过拟合）
model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# 预测和评估
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"决策树模型在测试集上的准确率: {acc * 100:.2f}%")

