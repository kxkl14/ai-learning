import pandas as pd
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

print("--- 第一步：数据准备 ---")
# 加载数据（继续用你已经下载好的本地文件，或者用sns.load_dataset）
try:
    df = pd.read_csv("train.csv").rename(columns=str.lower)
    df = df.drop(columns=['name', 'ticket', 'cabin', 'passengerid'], errors='ignore')
except FileNotFoundError:
    df = sns.load_dataset('titanic')

# 清洗数据
df = df.drop(columns=['deck', 'embark_town', 'alive', 'who', 'adult_male', 'class'], errors='ignore')
df['age'] = df['age'].fillna(df['age'].median())
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
df = df.dropna()
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df = pd.get_dummies(df, columns=['embarked'], drop_first=True)

# 划分数据
X = df.drop('survived', axis=1)
y = df['survived']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练昨天的决策树模型
tree_model = DecisionTreeClassifier(max_depth=3, random_state=42)
tree_model.fit(X_train, y_train)
tree_preds = tree_model.predict(X_test)

print("\n--- 第二步：混淆矩阵 ---")
cm = confusion_matrix(y_test, tree_preds)
print("混淆矩阵:\n", cm)
print(f"测试集真实情况: {cm[0][0]+cm[0][1]} 人遇难， {cm[1][0]+cm[1][1]} 人幸存。")
print(f"模型预测: 把 {cm[0][0]} 人正确预测为遇难，把 {cm[1][1]} 人正确预测为幸存。")
print(f"错误预测: 把 {cm[0][1]} 个遇难者错判成了幸存者，把 {cm[1][0]} 个幸存者误判成了遇难者。")

print("\n--- 第三步：特征重要性 ---")
# 把特征的重要程度提取出来，按从高到低排列
importances = pd.Series(tree_model.feature_importances_, index=X.columns)
print(importances.sort_values(ascending=False))

from sklearn.ensemble import RandomForestClassifier

print("\n--- 第四步：随机森林模型 ---")
# 建立包含100棵树的森林，每棵树最深5层
rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf_model.fit(X_train, y_train)

rf_preds = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_preds)
print(f"随机森林在测试集上的准确率: {rf_acc * 100:.2f}%")
