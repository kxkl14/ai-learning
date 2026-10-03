# 第一课：变量和类别

name = "gaole"                #字串符 （字串符必须用引号包起来）
age = 25                      #整数   （不带小数点）
height = 1.75                 #浮点数 （带小数点）
is_learning = True            #布尔值 （True或False）

print("姓名",name)
print("年龄",age)
print("身高",height)
print("正在学习",is_learning)

#第二课： 接收用户输入并格式化
#input() 会让程序暂停，等你输入完毕后按回车
user_name = input("请输入你的名字")
user_age = input("请输入你的年龄")      #注意：input 拿到的默认是字串符，不是数字
user_hobby = input("请输入你的爱好")

#f-string: 在引号前加 f，用{}包裹变量，可以直接把变量塞进句子
message = f"大家好，我是{user_name},今年{user_age}岁，我的爱好是{user_hobby}。"
print(message)

#第二课： 互动名片生成器
user_name = input("请输入你的名字")
user_job = input("请输入你的职业")
user_city = input("请输入你的城市")

# f-string: 在引号前加 f，{}里放变量
card = f"""
===========个人名片============
姓名：{user_name}
职业：{user_job}
城市：{user_city}
===============================
"""
print(card)
