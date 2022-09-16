import time
import win32con, win32api
import win32clipboard as w
import uiautomation as auto
import subprocess
import numpy as np
import pyperclip


from time import sleep
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl
from typing import List


# 调用win32api的模拟点击功能实现ctrl+v粘贴快捷键
def ctrlV():
    win32api.keybd_event(17,0,0,0)  #ctrl键位码是17
    win32api.keybd_event(86,0,0,0)  #v键位码是86
    win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0) #释放按键
    win32api.keybd_event(17,0,win32con.KEYEVENTF_KEYUP,0)


# 鼠标移动到控件上
def move(element):
    x, y = element.GetPosition()
    auto.SetCursorPos(x, y)


# 鼠标快速点击控件
def click(element):
    x, y = element.GetPosition()
    auto.Click(x, y)


# 鼠标快速点击两下控件
def double_click(element):
    x, y = element.GetPosition()
    auto.SetCursorPos(x, y)
    element.DoubleClick()

# 微信的控件介绍
# 以群名“测试”为例
# 左侧聊天列表“测试”群               Name: '测试'     ControlType: ListItemControl    depth: 10
# 左侧聊天列表“测试”群               Name: '测试'     ControlType: ButtonControl      depth: 12
# 进入“测试”群界面后上方的群名        Name: '测试'     ControlType: ButtonControl      depth: 14
# “测试”群界面的内容框               Name: '消息'     ControlType: ListControl        depth: 12


class WeChat:
    def __init__(self, path):
        # 微信打开路径
        self.path = path

        # 用于复制内容到剪切板
        self.app = QApplication([])

        # 自动回复的联系人列表
        self.auto_reply_contacts = []

        # 自动回复的内容
        self.auto_reply_msg = "[自动回复]您好，我现在正在忙，稍后会主动联系您，感谢理解。"

    # 打开微信客户端
    def open_wechat(self):
        subprocess.Popen(self.path)

    # 搜寻微信客户端控件
    def get_wechat(self):
        return auto.WindowControl(Depth=1, Name="微信")

    # 搜索指定用户
    def get_contact(self, name):
        self.open_wechat()
        wechat = self.get_wechat()

        search_box = auto.EditControl(Depth=8, Name="搜索")
        click(search_box)

        pyperclip.copy(name)
        ctrlV()
        # 等待客户端搜索联系人
        time.sleep(0.1)
        search_box.SendKeys("{enter}")

    # 在指定群聊中@他人（若@所有人需具备@所有人权限）
    def at(self, name, at_name):
        self.get_contact(name)

        # 如果at_name为空则代表@所有人
        if at_name == "":
            auto.SendKeys("@{UP}{enter}{enter}")

        else:
            auto.SendKeys(f"@{at_name}")
            auto.SendKeys("{enter}{enter}")

    # 搜索指定用户名的联系人发送信息
    def send_msg(self, name, text):
        self.get_contact(name)
        pyperclip.copy(text)
        ctrlV()
        auto.SendKeys("{enter}")

    # 搜索指定用户名的联系人发送文件
    def send_file(self, name, path):
        # 粘贴文件发送给用户
        self.get_contact(name)
        # 将文件复制到剪切板
        file = QMimeData()
        url = QUrl.fromLocalFile(path)
        file.setUrls([url])
        self.app.clipboard().setMimeData(file)

        # 暂停等待文件复制到剪切板
        time.sleep(0.5)
        ctrlV()
        auto.SendKeys("{enter}")

    # 获取所有通讯录中所有联系人
    def find_all_contacts(self):
        self.open_wechat()
        self.get_wechat()

        # 获取通讯录管理界面
        click(auto.ButtonControl(Name="通讯录"))
        list_control = auto.ListControl(Name="联系人")
        scroll_pattern = list_control.GetScrollPattern()
        scroll_pattern.SetScrollPercent(-1, 0)
        contacts_menu = list_control.ButtonControl(Name="通讯录管理")
        click(contacts_menu)

        # 切换到通讯录管理界面
        contacts_window = auto.GetForegroundControl()
        list_control = contacts_window.ListControl()
        scroll_pattern = list_control.GetScrollPattern()

        # 读取用户
        contacts = []
        for percent in np.arange(0, 1.05, 0.05):
            scroll_pattern.SetScrollPercent(-1, percent)
            for contact in contacts_window.ListControl().GetChildren():
                # 获取用户的昵称以及备注
                name = contact.TextControl().Name
                note = contact.ButtonControl(foundIndex=2).Name

                # 有备注的用备注，没有备注的用昵称
                if note == "":
                    contacts.append(name)
                else:
                    contacts.append(note)

        # 返回去重过后的联系人列表
        return list(set(contacts))

    # 检测微信是否收到新消息
    def check_new_msg(self):
        self.open_wechat()
        self.get_wechat()

        # 获取左侧聊天按钮
        chat_btn = auto.ButtonControl(Name="聊天")
        item = auto.ListItemControl()
        double_click(chat_btn)
        # 持续点击聊天按钮，直到获取完全部新消息
        first_name = item.Name
        while True:
            print(item.Name)
            # 判断该联系人是否需要自动回复
            if item.Name in self.auto_reply_contacts:
                self.auto_reply(item, self.auto_reply_msg)
                # print("需要自动回复")

            # 跳转到下一个新消息
            double_click(chat_btn)
            item = auto.ListItemControl()
            # 已经完成遍历，退出循环
            if first_name == item.Name:
                break

    # 设置自动回复的联系人
    def set_auto_reply(self, contacts):
        # contacts是一个列表
        self.auto_reply_contacts = contacts

    # 自动回复
    def auto_reply(self, element, text):
        click(element)
        pyperclip.copy(text)
        ctrlV()
        element.SendKeys("{enter}")
    
    # 识别聊天内容的类型
    # 0：用户发送    1：时间信息  2：红包信息  3：”查看更多消息“标志
    def _detect_type(self, list_item_control: auto.ListItemControl) -> int:
        value = None
        # 判断内容框是否为时间框，如果是时间框则列表为空
        if len(list_item_control.PaneControl().GetChildren()) == 0:
            value = 1

        else:
            cnt = 0
            for child in list_item_control.PaneControl().GetChildren():
                cnt += len(child.GetChildren())
                
            # 判断是否为用户发送的信息
            if cnt > 0:
                value = 0
            # 判断是否为“查看更多消息”
            elif list_item_control.Name == "查看更多消息":
                value = 3
            # 或者是红包信息
            elif "红包" in list_item_control.Name:
                value = 2
           
        return value
    
    # 获取聊天窗口
    def _get_chat_frame(self, name: str):
        self.get_contact(name)
        return auto.ListControl(Name="消息")
    
    # 获取指定聊天窗口的聊天记录
    def get_dialogs(self, name: str, n_msg: int) -> List:
        """
        Args:
            name: 聊天窗口的姓名
            n_msg: 获取聊天记录的最大数量（从最后一条往上算）
        
        Return:
            dialogs: 聊天记录列表，内部元素为三元组（信息类型，发送人，发送内容）
        """
        list_control = self._get_chat_frame(name)
        scroll_pattern = list_control.GetScrollPattern()
        
        # 如果聊天记录数量 < n_msg，则继续往上翻直到满足条件或无法上翻为止
        while len(list_control.GetChildren()) < n_msg:
            # 将聊天记录翻到“查看更多消息”
            scroll_pattern.SetScrollPercent(-1, 0)
            # 如果无法上翻则退出
            first_item = list_control.GetFirstChildControl()
            if self._detect_type(first_item) != 3:
                break
            # 否则点击“查看更多消息”
            else:
                click(first_item)
        
        cnt = 0
        dialogs = []
        value_to_info = {0: '用户发送', 1: '时间信息', 2: '红包信息', 3: '"查看更多消息"标志'}
        # 从下往上依次记录聊天内容。
        for list_item_control in list_control.GetChildren()[::-1]:
            v = self._detect_type(list_item_control)
            msg = list_item_control.Name
            name = list_item_control.ButtonControl().Name if v == 0 else ''

            cnt += 1
            dialogs.append((value_to_info[v], name, msg))
            
            # 如果达到n_msg则退出
            if cnt == n_msg:
                break
        
        # 将聊天记录列表翻转
        dialogs = dialogs[::-1]
        return dialogs


if __name__ == '__main__':
    wechat_path = "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    wechat = WeChat(wechat_path)

    name = ""
    text = ""
    
    dialogs = wechat.get_dialogs(name, 30)
    # wechat.send_msg(to_who, text)

    # contacts = wechat.find_all_contacts()
    # print(contacts)
