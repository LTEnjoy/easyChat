#此文件定义ui的一些辅助计算以及联通ui与其他
import time
import os

from configparser import ConfigParser
from ui_auto_wechat import WeChat


# 操作配置文件
class Conf():
    # 生成配置列表
    def readConfig():
        main_path0=os.path.dirname(__file__)    # 读取当前.py文件的相对路径
        main_path=os.path.abspath(main_path0)   # 返回文件的绝对路径
        config = ConfigParser()
        config.read(main_path+r'\res\config.txt',encoding="utf-8-sig")    # 读取配置文件
        confList = [config.get('conf0', 'WeChatPath'),config.get('conf0', 'FriendPath'),config.get('conf0', 'MsgPath')]    # 构建配置列表
        return(confList)


# 时间操作的类
class Clock():
    # 验证时间格式是否正确
    def checkTime(timeList):
        # 验证时间格式
        for timeLine in timeList:
            # 验证时间是否为整数且大于4位
            try:
                timeLine = timeLine.split(" ")
                timeLine[0] = int(timeLine[0])
                timeLine[1] = int(timeLine[1])
                timeLine[2] = int(timeLine[2])
                timeLine[3] = int(timeLine[3])
            except:
                return(False)
            # 检查小时是否在范围内
            if timeLine[0]<0 and timeLine[0]>24:
                return(False)
            # 检查分钟是否在范围内
            if timeLine[1]<0 and timeLine[1]>=60:
                return(False)
            # 进一步排除24点xx分的输入
            if timeLine[0] ==24 and timeLine[1] != 0:
                return(False)
        return(True)
    
    # 对时间进行格式修正
    def stands(timeLine,msgList):
        i = timeLine.split(" ")    # 分割时间
        st = int(i[2])
        ed = int(i[3])
        #修正起止条目
        st = abs(st)
        ed = abs(ed)
        if st > ed:
            a = st
            st = ed
            ed = a
        if ed > len(msgList):
            ed = len(msgList)
        return(st,ed)
    
    # 计算休眠时间
    def count(timeLine):
        timeLine = timeLine.split(" ")
        localtime = time.localtime(time.time())
        startTime = localtime.tm_hour * 3600 + localtime.tm_min * 60
        endTime = int(timeLine[0]) * 3600 + int(timeLine[1]) * 60
        sleepTime = endTime - startTime - 50
        if sleepTime < 0:
            sleepTime = 0.5
        return(sleepTime)


#  操作微信的类  
class chat():
    # 获取联系人列表
    def getContacts():
        wechatPath = Conf.readConfig()[0]
        wechat = WeChat(wechatPath)
        contactList = wechat.find_all_contacts()
        contacts = '\n'.join(contactList)
        return(contacts)
    
    # 发送消息
    def send(nameList,msgList,timeLine):
        print("开始发送")
        st,ed = Clock.stands(timeLine,msgList)    # 修正消息起止点
        print(st,ed)
        wechatPath = Conf.readConfig()[0]
        wechat = WeChat(wechatPath)
        for name in nameList:
            # 在此处进行搜索操作较为合理
            for i in range(st-1,ed):
                msg = msgList[i]
                wechat.send_msg(name,msg)
        return() # 暂未添加返回值识别