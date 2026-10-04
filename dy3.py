# 第一课：条件判断
import random
print("--- 成绩等级判定器 ---")
score = int(input("请输入你的成绩："))    # 注意 int(), 把输入的字符串转成整数

if score >= 90:
    print("优秀！")
elif score >= 80:                        # elif 是 eise if 的缩写
    print("良好")
elif score >= 60:
    print("及格")
else:                                    # 以上都不满足时执行
    print("不及格，请继续努力!")

# 第二课：循环
print("--- 循环打印1到5 ---")

# 1. for 循环：知道要循环多少次时使用
for i in range(1,6):                     # range（1，6） 会生成1，2，3，4，5
    print("for循环打印：",i)

# 2. while 循环：不知道要循环多少次，直到条件不满足时用
print("--- 倒计时 ---")
count = 3
while count > 0:
    print(count)
    count = count - 1                    # 每次减1，否则会变成无限死循环
print("发射！")

# 第三课：综合小项目 - 猜数字游戏
print("--- 猜数字游戏 ---")
secret = random.randint(1,10)            # 随机生成1到10之间的整数
guess = 0
tries = 0

while guess != secret:                   # 只要没猜对，就一直循环
    guess = int(input("请输入你猜的数字(1-10)"))
    tries = tries + 1                    # 记录猜测次数

    if guess > secret:
        print("猜大了，再试试！")
    elif guess < secret:
        print("猜小了，再试试！")
    else:
        print(f"太棒了！你猜对了{tries}次就对了，答案就是{secret}!")
        
        



