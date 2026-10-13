from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

print("--- 第一步：加载和划分数据 ---")
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("--- 第二步：搜索不同的 K 值（邻居数量） ---")
# 尝试 K = 1，3，5，10，20，看看准确率怎么变
for k in [1, 3, 5, 10, 20]:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"K={k:2d} | 测试集准确率: {acc*100:.2f}%")

print("\n--- 第三步：使用交叉验证 (5折) ---")
# 依然用 K=3 模型
model = KNeighborsClassifier(n_neighbors=3)

# cv=5 表示进行5折交叉验证
# 注意：这里直接把完整的 X 和 y 传进去，交叉验证会自动帮我们划分
cv_scores = cross_val_score(model, X, y, cv=5)

print(f"5次测试的准确率: {cv_scores * 100}")
print(f"平均准确率: {cv_scores.mean()*100:.2f}%")

