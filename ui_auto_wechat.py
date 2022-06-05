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


# 调用win32api的模拟点击功能实现ctrl+v粘贴快捷键
def ctrlV():
    win32api.keybd_event(17,0,0,0)  #ctrl键位码是17
    win32api.keybd_event(86,0,0,0)  #v键位码是86
    win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0) #释放按键
    win32api.keybd_event(17,0,win32con.KEYEVENTF_KEYUP,0)


# 鼠标快速点击控件
def click(element):
    x, y = element.GetPosition()
    auto.Click(x, y)


class WeChat():
    def __init__(self, path):
        # 微信打开路径
        self.path = path

        # 用于复制内容到剪切板
        self.app = QApplication([])

    # 打开微信客户端
    def open_wechat(self):
        subprocess.Popen(self.path)

    # 搜寻微信客户端控件
    def get_wechat(self):
        return auto.WindowControl(searchDepth=1, Name="微信")

    # 进入指定用户窗口
    def get_contact(self, name):
        self.open_wechat()
        wechat = self.get_wechat()

        search_box = wechat.EditControl(searchDepth=8, Name="搜索")
        click(search_box)

        pyperclip.copy(name)
        ctrlV()
        # 等待客户端搜索联系人
        time.sleep(0.1)
        # search_box.SendKeys(name, interval=0.1)
        search_box.SendKeys("{enter}")

        return search_box

    # 搜索指定用户名的联系人发送信息
    def send_msg(self, name, text):
        window = self.get_contact(name)
        pyperclip.copy(text)
        ctrlV()
        window.SendKeys("{enter}")

    # 搜索指定用户名的联系人发送文件
    def send_file(self, name, path):
        # 粘贴文件发送给用户
        window = self.get_contact(name)
        # 将文件复制到剪切板
        file = QMimeData()
        url = QUrl.fromLocalFile(path)
        file.setUrls([url])
        self.app.clipboard().setMimeData(file)

        # 暂停等待文件复制到剪切板
        time.sleep(0.5)
        ctrlV()
        window.SendKeys("{enter}")

    # 获取所有通讯录中所有联系人
    def find_all_contacts(self):
        self.open_wechat()
        wechat = self.get_wechat()

        # 获取通讯录管理界面
        click(wechat.ButtonControl(Name="通讯录"))
        list_control = wechat.ListControl(Name="联系人")
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

                print(name,  note)
                # 有备注的用备注，没有备注的用昵称
                if note == "":
                    contacts.append(name)
                else:
                    contacts.append(note)

        # 返回去重过后的联系人列表
        return list(set(contacts))

    # # 检测微信是否收到新消息
    # def check_new_msg(self):
    #     self.open_wechat()
    #     wechat = self.get_wechat()
    #     item = wechat.ListItemControl(Name="")
    #     x, y = item.GetPosition()
    #     auto.MoveTo(x, y)
    #     print(item.TextControl(Depth=2))


if __name__ == '__main__':
    wechat_path = "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    wechat = WeChat(wechat_path)

    to_who = "文件"
    text = "你好"
    file_path = r""
    # for contact in [to_who]:
    #     wechat.send_file(contact, file_path)

    # wechat.check_new_msg()
    # auto.ShowDesktop()
    # auto.Click(200, 200)
    # print("\U0001f4a3")
