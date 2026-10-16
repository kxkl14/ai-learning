import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("--- 第一步：数据准备 ---")
# 读取本地数据，并顺手把列名转成小写
df = pd.read_csv("train.csv").rename(columns=str.lower)
df = df.drop(columns=['name', 'ticket', 'cabin', 'passengerid'], errors='ignore')

# 清洗数据
df['age'] = df['age'].fillna(df['age'].median())
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
df = df.dropna()
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df = pd.get_dummies(df, columns=['embarked'], drop_first=True)

X = df.drop('survived', axis=1)
y = df['survived']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练基础随机森林模型
base_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
base_model.fit(X_train, y_train)
base_acc = accuracy_score(y_test, base_model.predict(X_test))
print(f"基础随机森林准确率: {base_acc * 100:.2f}%")

print("\n--- 第二步：模型持久化 ---")
# 1. 把训练好的模型保存为 .pkl 文件
joblib.dump(base_model, "titanic_rf_model.pkl")
print("模型已保存为 titanic_rf_model.pkl")

# 2. 模拟“下次打开电脑”：直接加载模型，不再重新训练
loaded_model = joblib.load("titanic_rf_model.pkl")
loaded_preds = loaded_model.predict(X_test)
loaded_acc = accuracy_score(y_test, loaded_preds)
print(f"加载模型后的预测准确率: {loaded_acc * 100:.2f}%(应当与基础模型一摸一样)")


print("\n--- 第三步：网络搜索自动调参 ---")
# 定义我们要尝试的参数范围
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, 10],
    'min_samples_split': [2, 5, 10]
}

# 建立网格搜索对象，cv=3 表示3折交叉验证
grid_search = GridSearchCV(estimator=RandomForestClassifier(random_state=42),
                           param_grid=param_grid,
                           cv=3,
                           scoring='accuracy',
                           n_jobs=-1)         # n_jobs=-1 表示用满 cpu 的所有核心加速训练

print("开始调参（可能需要运行 30 秒左右，请耐心等待）...")
grid_search.fit(X_train, y_train)

print(f"最佳参数组合: {grid_search.best_params_}")
print(f"网格搜索的最高准确率: {grid_search.best_score_ * 100:.2f}%")

# 用最佳模型在测试集上进行最终预测
best_model = grid_search.best_estimator_
final_acc = accuracy_score(y_test, best_model.predict(X_test))
print(f"最佳模型在测试集上的准确率: {final_acc * 100:.2f}%")