#!/usr/bin/python
# -*- coding: UTF-8 -*-
#软件的UI文件
import os
import time
import bridge
import pyperclip

from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtCore import *
from bridge import chat


# 运行信号
class RunSignals(QObject):
    finished = Signal()
    result = Signal(object)


# 新建一个线程执行发送程序
class RunSend(QRunnable):   
    def __init__(self,nameList,msgList,timeLine):
        super().__init__()
        self.signals = RunSignals()
        self.nameList = nameList
        self.msgList = msgList
        self.timeLine = timeLine
            
    @Slot()
    def run(self):
        result = chat.send(self.nameList,self.msgList,self.timeLine)
        self.signals.result.emit(result)    # 发射运行结果信号
        self.signals.finished.emit()    #发送运行完成信号


#新建一个线程进行计时并发送
class ClockSend(QRunnable):
    def __init__(self,nameList,msgList,timeList):
        super().__init__()
        self.isRunning = True
        self.signals = RunSignals()
        self.nameList = nameList
        self.msgList = msgList
        self.timeList = timeList

    # 开始运行
    @Slot()
    def run(self):
        for timeLine in self.timeList:
            # 没有收到中断信号则开始计时
            self.sleepTime = bridge.Clock.count(timeLine)    #计算睡眠时间
            if self.isRunning:
                time.sleep(self.sleepTime)
            # 没有收到中断信号则开始发送
            if self.isRunning:
                self.sendThread = RunSend(self.nameList,self.msgList,timeLine) # 创建发送消息任务
                #self.sendThread.signals.result.connect(self.onResultSend)
                #self.sendThread.signals.finished.connect(self.onFinishSend)
                # 在新线程中启动CLockWorker
                QThreadPool.globalInstance().start(self.sendThread) # i在新线程池中启动发送
                QThreadPool.globalInstance().waitForDone()    # 等待新线程池中的所有任务完成
        self.signals.finished.emit()    #发送单次运行完成信号
    
    # 停止线程
    def stop(self):
        self.sleepTime = 0.1
        self.isRunning = False


# 主窗口
class MainWindow:
    def __init__(self):
        mainPath0 = os.path.dirname(__file__)    # 读取当前.py文件的父文件相对路径
        mainPath = os.path.abspath(mainPath0)    # 返回文件的绝对路径
        self.configPath = os.path.join(mainPath,'res','config.txt')
        uiPath = os.path.join(mainPath,'res','mainwindow.ui')   # 构造ui文件的绝对路径
        self.ui = QUiLoader().load(uiPath)    # 读取ui文件
        self.sendThread = None    # 定义一个运行程序的线程
        self.clockSendThread = None    # 定义一个定时发送的线程
        self.threadPool = QThreadPool()   # 创建线程池
        
        #绑定按钮与功能
        self.ui.btn_getUsers.clicked.connect(self.btn_getUsers)
        self.ui.btn_setting.clicked.connect(self.btn_setting)        # 设置

        self.ui.btn_send.clicked.connect(self.btn_send)        # 开始发送
        self.ui.btn_addUsers.clicked.connect(self.btn_addUsers)        # 批量添加用户
        self.ui.btn_delUser.clicked.connect(self.btn_delUser)        # 清空用户列表
        self.ui.btn_addFile.clicked.connect(self.btn_addFile)    # 添加文件
        self.ui.btn_addPreMsg.clicked.connect(self.btn_addPreMsg)    # 导入预设消息
        self.ui.btn_delMsg.clicked.connect(self.btn_delMsg)    # 清空消息列表
        self.ui.btn_delTime.clicked.connect(self.btn_delTime)    # 开始定时
        self.ui.btn_endTime.clicked.connect(self.btn_endTime)    # 结束定时

    
    # 获取用户列表并复制到剪贴板
    def btn_getUsers(self):
        note = QMessageBox()
        #try:
        contacts = chat.getContacts()
        pyperclip.copy(contacts)
        note.setText('联系人已复制到剪贴板')    
        #except:
        #    note.setText('复制失败')
        note.setWindowFlags(Qt.WindowStaysOnTopHint)
        note.exec_()
    
    # 设置按钮响应事件
    def btn_setting(self):    
        try:    
            os.startfile(self.configPath)
        except:
            print("错误：打开配置文件失败")
            return
        
    # 批量添加用户按钮响应事件
    def btn_addUsers(self):    
        self.filePath = self.confs[1]
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath,"*.txt") # 起始路径
        file = open(path[0],encoding="utf-8")
        self.ui.textEdit_users.append(file.read())
        file.close()

    # 清空用户列表按钮响应事件
    def btn_delUser(self):    
        self.ui.textEdit_users.clear()

    # 添加文件按钮响应事件
    def btn_addFile(self):    
        self.filePath = "C:\\"
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath) # 起始路径
        if path[0] != "":
            self.ui.textEdit_msg.append("|\n"+path[0]+"|\n")

    # 导入预设消息按钮响应事件
    def btn_addPreMsg(self):    
        self.filePath = self.confs[2]
        path = QFileDialog.getOpenFileName(None, "选择文件", self.filePath,"*.txt") # 起始路径
        file = open(path[0],encoding="utf-8")
        self.ui.textEdit_msg.append(file.read())
        file.close()

    # 清空消息列表按钮响应事件
    def btn_delMsg(self):    
        self.ui.textEdit_msg.clear()
    
    # 开始定时按钮响应事件
    def btn_delTime(self):
        self.ui.textEdit_time.clear()
    
    # 结束定时按钮响应事件
    def btn_endTime(self):
        self.ui.label_clock.setStyleSheet("color:black")
        self.ui.label_clock.setText("定时发送未启动") 
        self.clockSendThread.stop()

     # 开始发送按钮响应事件
    def btn_send(self):    
        self.nameList = self.ui.textEdit_users.toPlainText().split("\n")    # 构造用户列表
        self.msgList = self.ui.textEdit_msg.toPlainText().split("|\n")    # 构造消息列表
        self.timeList = self.ui.textEdit_time.toPlainText().split("\n")    # 构造时间列表
        # 如果定时列表为空,直接启动发送线程
        if self.timeList == ['']:
            # 创建一个新的SendThread并将参数传给它
            timeLine = "0 0 1 "+str(len(self.msgList))
            self.sendThread = RunSend(self.nameList,self.msgList,timeLine) # 创建发送消息任务
            self.sendThread.signals.result.connect(self.onResultSend)
            self.sendThread.signals.finished.connect(self.onFinishSend)
            # 在新线程中启动CLockWorker
            self.threadPool.start(self.sendThread) # 在线程池中启动发送
        # 如果定时列表非空，进行定时发送
        elif bridge.Clock.checkTime(self.timeList):    # 如果格式验证通过
            self.timeList = sorted(self.timeList, key=lambda x: int(x.split(" ")[1]))    # 对时间列表排序
            self.timeList = sorted(self.timeList, key=lambda x: int(x.split(" ")[0]))    # 对时间列表排序
            self.ui.label_clock.setStyleSheet("color:green")
            self.ui.label_clock.setText("定时发送已启动")
            # 创建发送消息任务并传递timeList
            self.clockSendThread = ClockSend(self.nameList,self.msgList,self.timeList)
            self.clockSendThread.signals.finished.connect(self.onFinishClock)
            # 在新线程中启动CLockWorker
            self.threadPool.start(self.clockSendThread) # 在线程池中启动发送
        else:
            self.ui.textEdit_time.append("格式有误，请检查")

    # 收到发送线程的反馈后执行
    @Slot(object)
    def onResultSend(self):    
        pass
    
    # 发送线程运行完毕后执行
    @Slot()
    def onFinishSend(self):
        pass

    # 接到定时发送完成信号后执行
    @Slot()
    def onFinishClock(self):
        self.ui.label_clock.setStyleSheet("color:black")
        self.ui.label_clock.setText("定时发送未启动")

if __name__ == "__main__":    #当直接运行此文件时执行下列命令
    app = QApplication([])
    stats = MainWindow()
    stats.ui.show()    #显示ui
    app.exec_()        #无限循环运行