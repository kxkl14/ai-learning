import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("--- Day 16: 本地文件读取版 ---")

# 1. 读取本地 train.csv
file_path = "train.csv"
if not os.path.exists(file_path):
    print(f"⚠️ 找不到 {file_path}，请确认终端当前路径下有这个文件！")
else:
    # 读取并自动把列名转成小写，防止大小写报错
    df = pd.read_csv(file_path).rename(columns=str.lower)
    
    # --- 超级容错补丁：如果下载的文件缺列，自动补齐 ---
    if 'embarked' not in df.columns:
        df['embarked'] = 'S'  # 补齐缺失的登船港口
    if 'sex' not in df.columns:
        df['sex'] = 'male'
    if 'age' not in df.columns:
        df['age'] = 30.0
    if 'fare' not in df.columns:
        df['fare'] = 50.0
    if 'survived' not in df.columns:
        raise ValueError("严重错误：文件里连 'survived' 标签都没有，无法训练！")

    # 2. 提取我们需要的数据列 (根据本地实际情况筛选)
    # 如果有 sibsp 和 parch 就加进来，没有就算了
    cols_to_keep = ['survived', 'pclass', 'sex', 'age', 'fare', 'embarked']
    if 'sibsp' in df.columns and 'parch' in df.columns:
        df['family_size'] = df['sibsp'] + df['parch'] + 1
        cols_to_keep.append('family_size')
        
    df = df[cols_to_keep].copy()

    # 3. 清洗数据
    df['age'] = df['age'].fillna(df['age'].median())
    df['fare'] = df['fare'].fillna(df['fare'].median())
    df['embarked'] = df['embarked'].fillna('S')

    # 4. 文字转数字
    df['sex'] = df['sex'].map({'male': 0, 'female': 1})
    # 自动处理 embarked，防止因为只有一个类别导致 get_dummies 报错
    df = pd.get_dummies(df, columns=['embarked'], drop_first=True)

    # 5. 划分数据
    X = df.drop('survived', axis=1)
    y = df['survived']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. 自动调参
    print("\n正在寻找最佳参数，请稍候...")
    param_grid = {'max_depth': [5, 7, 10], 'n_estimators': [100, 200]}
    final_model = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, n_jobs=-1)
    final_model.fit(X_train, y_train)

    # 7. 评估
    best_model = final_model.best_estimator_
    print(f"最佳参数: {final_model.best_params_}")
    print(f"测试集准确率: {accuracy_score(y_test, best_model.predict(X_test)) * 100:.2f}%")

    # 8. 保存模型
    joblib.dump(best_model, "titanic_final_model.pkl")
    print("模型已保存为 titanic_final_model.pkl")

    # 9. 加载模型并预测
    print("\n--- 预测新乘客 ---")
    loaded_model = joblib.load("titanic_final_model.pkl")

    # 动态生成新乘客的特征，防止因列数不对报错
    # 构造一个 30岁、头等舱、女性、票价100的数据
    new_data = {col: 0 for col in X.columns} # 先全部初始化为0
    new_data['pclass'] = 1
    new_data['sex'] = 1
    new_data['age'] = 30.0
    new_data['fare'] = 100.0
    if 'family_size' in new_data:
        new_data['family_size'] = 1

    new_passenger = pd.DataFrame([new_data], columns=X.columns)
    pred = loaded_model.predict(new_passenger)

    if pred[0] == 1:
        print("预测结果：这位乘客【幸存】！")
    else:
        print("预测结果：这位乘客【遇难】...")