import time

import win32con, win32api
import win32clipboard as w
import uiautomation as auto
import subprocess
from time import sleep


# 调用win32api的模拟点击功能实现ctrl+v粘贴快捷键
def ctrlV():
    win32api.keybd_event(17,0,0,0)  #ctrl键位码是17
    win32api.keybd_event(86,0,0,0)  #v键位码是86
    win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0) #释放按键
    win32api.keybd_event(17,0,win32con.KEYEVENTF_KEYUP,0)


class WeChat():
    def __init__(self, path):
        # 微信打开路径
        self.path = path

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
        search_box.Click()

        search_box.SendKeys(name, interval=0.1)
        search_box.SendKeys("{enter}")

        return search_box

    # 搜索指定用户名的联系人发送信息
    def send_msg(self, name, text):
        window = self.get_contact(name)
        window.SendKeys(text)
        window.SendKeys("{enter}")

    # 搜索指定用户名的联系人发送文件
    def send_file(self, name):
        window = self.get_contact(name)
        ctrlV()
        window.SendKeys("{enter}")


if __name__ == '__main__':
    wechat_path = "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    wechat = WeChat(wechat_path)

    to_who = "四片打流小分队"
    text = "你好"

    for contact in [to_who]:
        wechat.send_file(contact)