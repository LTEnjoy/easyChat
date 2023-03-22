#!/usr/bin/python
# -*- coding: UTF-8 -*-
#软件的UI文件
import os
import sys
import time

from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtCore import *
from configparser import ConfigParser
from ui_auto_wechat import WeChat


class Conf():  # 操作配置文件
    def readConfig():    # 读取配置文件
        main_path0=os.path.dirname(__file__)    # 读取当前.py文件的相对路径
        main_path=os.path.abspath(main_path0)   # 返回文件的绝对路径
        config = ConfigParser()
        config.read(main_path+r'\res\config.txt',encoding="utf-8-sig")
        confList = [config.get('conf0', 'WeChatPath'),config.get('conf0', 'FriendPath'),config.get('conf0', 'MsgPath'),config.get('conf0', 'SendMode')]    #构建配置列表
        return(confList)
    

class ClockThread(QThread):    # 定时发送子线程类
    def __init__(self):
        super().__init__()
        # 是否正在定时
        self.time_counting = False
        # 发送信息的函数
        self.send_func = None
        # 定时列表
        self.clocks = None

    def __del__(self):
        self.wait()

    def run(self):
        while self.time_counting:
            localtime = time.localtime(time.time())
            hour = localtime.tm_hour % 24
            min = localtime.tm_min % 60

            #验证时间列表,这里想抓取主窗口的数据，验证后再执行并改变主窗口的显示，不会多线程，完全不知道怎么写。
            try:
                timeList = Stats.ui.textEdit_time.toPlainText().split("\n")    # 从主窗口中提取数据构造时间列表
                for timeLine in timeList:    # 验证每一行时间格式是否正确
                    timeLine = timeLine.toPlainText().split(" ")
                    timeLine[0] = int(timeLine[0])
                    timeLine[1] = int(timeLine[1])
                    timeLine[2] = int(timeLine[2])
                    timeLine[3] = int(timeLine[3])
                    timeLine[0]>=1 and timeLine[0]<=24
                    timeLine[1]>=0 and timeLine[1]<=60
            except:
                Stats.ui.textEdit_time.setText("无效的时间格式，请重新输入")
                return

            #发送消息
            Stats.ui.label_3.setStyleSheet("color:red")    # 修改UI显示状态
            Stats.ui.label_3.setText("定时发送(用回车分隔)\n（已开启）")
            msgList = Stats.ui.textEdit_msg.toPlainText().split("|\n")    # 构造消息列表
            for i in timeList:
                st = i[2]
                if st <=0:
                    st = 1
                ed = i[3]
                if ed > len(msgList):
                    ed = len(msgList)
                self.send_func(st=int(st), ed=int(ed))
            time.sleep(60)


class Stats:    # 主窗口
    def __init__(self):
        mainPath0 = os.path.dirname(__file__)    # 读取当前.py文件的父文件相对路径
        mainPath = os.path.abspath(mainPath0)    # 返回文件的绝对路径
        self.configPath = os.path.join(mainPath,'res','config.txt')
        uiPath = os.path.join(mainPath,'res','mainwindow.ui')   # 构造ui文件的绝对路径
        self.ui = QUiLoader().load(uiPath)    # 读取ui文件
        self.confs = Conf.readConfig()    # 读取配置文件
        self.wechat = WeChat(None)    # 引用微信
        self.clock = ClockThread()    # 设置定时
        self.clock.send_func = self.btn_send    # 启动定时
        self.wechat.path = self.confs[0]    # 导入微信路径
        
        #绑定按钮与功能
        self.ui.btn_send.clicked.connect(self.btn_send)        # 开始发送
        self.ui.btn_setting.clicked.connect(self.btn_setting)        # 设置
        self.ui.btn_addUsers.clicked.connect(self.btn_addUsers)        # 批量添加用户
        self.ui.btn_delUser.clicked.connect(self.btn_delUser)        # 清空用户列表
        self.ui.btn_addFile.clicked.connect(self.btn_addFile)    # 添加文件
        self.ui.btn_addPreMsg.clicked.connect(self.btn_addPreMsg)    # 导入预设消息
        self.ui.btn_delMsg.clicked.connect(self.btn_delMsg)    # 清空消息列表
        self.ui.btn_startTime.clicked.connect(self.btn_startTime)    # 开始定时
        self.ui.btn_endTime.clicked.connect(self.btn_endTime)    # 结束定时


    # 设置按钮功能
    def btn_setting(self):    # 设置按钮响应事件
        try:    
            os.startfile(self.configPath)
        except:
            print("错误：无法打开配置文件失败")
            return
        
    def btn_addUsers(self):    # 批量添加用户按钮响应事件
        self.filePath = self.confs[1]
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath,"*.txt") # 起始路径
        file = open(path[0],encoding="utf-8")
        self.ui.textEdit_users.append(file.read())
        file.close()

    def btn_delUser(self):    # 清空用户列表按钮响应事件
        self.ui.textEdit_users.clear()

    def btn_addFile(self):    # 添加文件按钮响应事件
        self.filePath = "C:\\"
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath) # 起始路径
        if path[0] != "":
            self.ui.textEdit_msg.append("|\n"+path[0]+"|\n")

    def btn_addPreMsg(self):    # 导入预设消息按钮响应事件
        self.filePath = self.confs[2]
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath,"*.txt") # 起始路径
        file = open(path[0],encoding="utf-8")
        self.ui.textEdit_msg.append(file.read())
        file.close()

    def btn_delMsg(self):    # 清空消息列表按钮响应事件
        self.ui.textEdit_msg.clear()

    def btn_startTime(self):    # 开始定时按钮响应事件
        userList = self.ui.textEdit_users.toPlainText().split("\n")    # 构造用户列表
        msgList = self.ui.textEdit_msg.toPlainText().split("|\n")    # 构造消息列表
        if self.clock.time_counting is True:
            return
        else:
            self.clock.time_counting = True
        self.clock.start()

    def btn_endTime(self):    # 结束定时按钮响应事件
        self.clock.time_counting = False
        self.ui.label_3.setStyleSheet("color:black")
        self.ui.label_3.setText("定时发送(用回车分隔)\n（格式示例“17 30 1 3”即17:30发送第1条至第3条）")

    def btn_send(self,gap=None, st=None, ed=None):     # 开始发送按钮响应事件
        # 如果未定义范围的开头和结尾，则默认发送全部信息
        userList = self.ui.textEdit_users.toPlainText().split("\n")    # 构造用户列表
        msgList = self.ui.textEdit_msg.toPlainText().split("|\n")    # 构造消息列表
        print(msgList)
        if st is None:
            st = 1
            ed = len(msgList)
        # 逐人逐条发送消息
        for name in userList:
            for msg in msgList[st-1:ed]:
                if os.path.isfile(msg):     # 判断为文件内容
                    self.wechat.send_file(name,msg)
                #elif msg[0] == "@":    # 判断为@他人
                #    self.wechat.at(name,msg[1:])
                else:    # 其余作为普通消息发送
                    print(msg)
                    if msg == None or msg == "\n":    # 跳过空白信息
                        continue
                    self.wechat.send_msg(name,msg)


if __name__ == "__main__":    #当直接运行此文件时执行下列命令
    app = QApplication([])
    stats = Stats()
    stats.ui.show()    #显示ui
    app.exec_()        #无限循环运行