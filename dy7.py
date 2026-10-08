import numpy as np    # 导入numpy，惯例简写为 np

print("--- 第一课：创建数组 ---")
# 1. 从 python 列表创建
arr1 = np.array([1, 2, 3, 4, 5])
print("arr1:", arr1) 

# 2. 生成常用数组
zeros = np.zeros(5)      # 全0数组
ones = np.ones(3)        # 全1数组
arange_arr = np.arange(0, 10, 2)    # 类似于 range，[0, 2, 4, 6, 8] 
print("全0:", zeros)
print("全1:", ones)
print("arange步长为2:", arange_arr)

print("\n--- 第二课：向量化运算 （比列表快几百倍） ---")
arr2 = np.array([10, 20, 30, 40, 50])

# 直接进行数学运算
print("相加:", arr1 + arr2)         # 对应元素相加
print("乘法:", arr1 * 2)            # 所有元素乘2
print("平方:", arr1 ** 2)           # 所有元素求平方

# 统计函数
print("求和:", arr1.sum())
print("平均值:", arr1.mean())
print("最大值:", arr1.max())

print("\n--- 第三课：属性与切片 ---")
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

print("矩阵:\n", matrix)
print("形状 (行，列):", matrix.shape)   # （3， 3）
print("维度:", matrix.ndim)            # 2
print("数据类型:", matrix.dtype)        # int32 或 int64

# 切片（跟列表类似，但可以多维切片）
print("第一行:", matrix[0])            # [1, 2, 3]
print("第一列:", matrix[:, 0])         # [1, 4, 7]
print("右下角2x2矩阵:\n", matrix[1:, 1:])

print("\n--- 第四课：实战矩阵乘法 ---")

# 2x2 矩阵
matrix_a = np.array([
    [1, 2],
    [3, 4]
])
matrix_b = np.array([
    [5, 6],
    [7, 8]
])

# 矩阵乘法（必须用 np.dot 或 @ 符号）
result = matrix_a @ matrix_b
print("矩阵A @ 矩阵B 的结果:\n", result)

# 广播机制 （比较难理解，但很强大）
# 一个 2x2 矩阵加上一个 1x2 的行向量，python 会自动把行向量复制两遍再相加
vector = np.array([10, 100])
print("矩阵A加上行向量(广播机制):\n", matrix_a + vector)
