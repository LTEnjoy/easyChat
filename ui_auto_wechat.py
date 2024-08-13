import time
import uiautomation as auto
import subprocess
import numpy as np
import pyperclip
import os
import pyautogui


from ctypes import *
from PIL import ImageGrab
from clipboard import setClipboardFiles
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl
from typing import List

from wechat_locale import WeChatLocale


# 鼠标移动到控件上
def move(element):
    x, y = element.GetPosition()
    auto.SetCursorPos(x, y)


# 鼠标快速点击控件
def click(element):
    x, y = element.GetPosition()
    auto.Click(x, y)


# 鼠标右键点击控件
def right_click(element):
    x, y = element.GetPosition()
    auto.RightClick(x, y)


# 鼠标快速点击两下控件
def double_click(element):
    x, y = element.GetPosition()
    auto.SetCursorPos(x, y)
    element.DoubleClick()


# 微信的控件介绍。注意"depth"是直接调用auto进行控件搜索的深度（见函数内部代码示例）
# 以群名“测试”为例：
# 左侧聊天列表“测试”群               Name: '测试'     ControlType: ListItemControl    depth: 10
# 左侧聊天列表“测试”群               Name: '测试'     ControlType: ButtonControl      depth: 12
# 进入“测试”群界面之后上方的群名       Name: '测试'     ControlType: ButtonControl      depth: 14
# “测试”群界面的内容框               Name: '消息'     ControlType: ListControl        depth: 12
# 聊天界面的聊天记录按钮              Name: '聊天记录'   ControlType: ButtonControl      depth: 14
# 聊天记录界面的图片按钮              Name: '图片与视频'     ControlType: TabItemControl      depth: 6
# 聊天记录复制图片按钮               Name: '复制'   ControlType: MenuItemControl      depth: 5


class WeChat:
    def __init__(self, path, locale="zh-CN"):
        # 微信打开路径
        self.path = path
        
        # 用于复制内容到剪切板
        self.app = QApplication([])
        
        # 自动回复的联系人列表
        self.auto_reply_contacts = []
        
        # 自动回复的内容
        self.auto_reply_msg = "[自动回复]您好，我现在正在忙，稍后会主动联系您，感谢理解。"
        
        self.lc = WeChatLocale(locale)
        
    # 打开微信客户端
    def open_wechat(self):
        subprocess.Popen(self.path)
    
    # 搜寻微信客户端控件
    def get_wechat(self):
        return auto.WindowControl(Depth=1, Name=self.lc.weixin)
    
    # 防止微信长时间挂机导致掉线
    def prevent_offline(self):
        self.open_wechat()
        self.get_wechat()
        
        search_box = auto.EditControl(Depth=8, Name=self.lc.search)
        click(search_box)
    
    # 搜索指定用户
    def get_contact(self, name):
        self.open_wechat()
        self.get_wechat()
        
        search_box = auto.EditControl(Depth=8, Name=self.lc.search)
        click(search_box)
        
        pyperclip.copy(name)
        auto.SendKeys("{Ctrl}v")
        # 等待客户端搜索联系人
        time.sleep(0.3)
        search_box.SendKeys("{enter}")
    
    # 鼠标移动到发送按钮处点击发送消息
    def press_enter(self):
        # 获取发送按钮
        send_button = auto.ButtonControl(Depth=15, Name=self.lc.send)
        click(send_button)
    
    def at(self, name, at_name, search_user: bool = True) -> None:
        """
        在指定群聊中@他人（若@所有人需具备@所有人权限）
        Args:
            name:  群聊名称
            at_name: 要@的人的昵称
            search_user: 是否需要搜索群聊
        """
        if search_user:
            self.get_contact(name)
        
        # 如果at_name为空则代表@所有人
        if at_name == "":
            auto.SendKeys("@{UP}{enter}")
            self.press_enter()
        
        else:
            auto.SendKeys(f"@{at_name}")
            # 按下回车键确认要at的人
            auto.SendKeys("{enter}")
            self.press_enter()
    
    def send_msg(self, name, text, search_user: bool = True) -> bool:
        """
        搜索指定用户名的联系人发送信息
        Args:
            name: 指定用户名的名称，输入搜索框后出现的第一个人
            text: 发送的文本信息
            search_user: 是否需要搜索用户
        """
        if search_user:
            self.get_contact(name)
        pyperclip.copy(text)

        # 等待粘贴
        time.sleep(0.3)
        auto.SendKeys("{Ctrl}v")

        self.press_enter()
        # 发送消息后马上获取聊天记录，判断是否发送成功
        if self.get_dialogs(name, 1,False)[0][2] == text:
            return True
        else:
            return False
    
    # 搜索指定用户名的联系人发送文件
    def send_file(self, name: str, path: str, search_user: bool = True) -> None:
        """
        Args:
            name: 指定用户名的名称，输入搜索框后出现的第一个人
            path: 发送文件的本地地址
            search_user: 是否需要搜索用户
        """
        if search_user:
            self.get_contact(name)
        
        # 将文件复制到剪切板
        setClipboardFiles([path])
        
        auto.SendKeys("{Ctrl}v")
        self.press_enter()
    
    # 获取所有通讯录中所有联系人
    def find_all_contacts(self):
        self.open_wechat()
        self.get_wechat()
        
        # 获取通讯录管理界面
        click(auto.ButtonControl(Name=self.lc.contacts))
        list_control = auto.ListControl(Name=self.lc.contact)
        scroll_pattern = list_control.GetScrollPattern()
        scroll_pattern.SetScrollPercent(-1, 0)
        contacts_menu = list_control.ButtonControl(Name=self.lc.manage_contacts)
        click(contacts_menu)
        
        # 切换到通讯录管理界面
        contacts_window = auto.GetForegroundControl()
        list_control = contacts_window.ListControl()
        scroll_pattern = list_control.GetScrollPattern()
        
        # 读取用户
        contacts = []
        # 如果不存在滑轮则直接读取
        if scroll_pattern is None:
            for contact in contacts_window.ListControl().GetChildren():
                # 获取用户的昵称以及备注
                name = contact.TextControl().Name
                note = contact.ButtonControl(foundIndex=2).Name

                # 有备注的用备注，没有备注的用昵称
                if note == "":
                    contacts.append(name)
                else:
                    contacts.append(note)
        else:
            for percent in np.arange(0, 1.002, 0.001):
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
    
    # 获取所有群聊
    def find_all_groups(self):
        self.open_wechat()
        self.get_wechat()
        
        # 获取通讯录管理界面
        click(auto.ButtonControl(Name=self.lc.contacts))
        list_control = auto.ListControl(Name=self.lc.contact)
        scroll_pattern = list_control.GetScrollPattern()
        scroll_pattern.SetScrollPercent(-1, 0)
        contacts_menu = list_control.ButtonControl(Name=self.lc.manage_contacts)
        click(contacts_menu)

        # 切换到通讯录管理界面
        contacts_window = auto.GetForegroundControl()
        
        # 点击最近群聊
        click(contacts_window.ButtonControl(Name="最近群聊"))
        
        # 获取群聊列表
        list_control = contacts_window.ListControl()
        scroll_pattern = list_control.GetScrollPattern()
        
        # 读取群聊
        contacts = []
        # 如果不存在滑轮则直接读取
        if scroll_pattern is None:
            for contact in contacts_window.ListControl().GetChildren():
                # 获取群聊的名称 (将所有的顿号替换成了空格，这样才能在搜索框搜索到)
                name = contact.TextControl().Name.replace("、", " ")
                contacts.append(name)

        else:
            for percent in np.arange(0, 1.002, 0.01):
                scroll_pattern.SetScrollPercent(-1, percent)
                for contact in contacts_window.ListControl().GetChildren():
                    # 获取群聊的名称 (将所有的顿号替换成了空格，这样才能在搜索框搜索到)
                    name = contact.TextControl().Name.replace("、", " ")
                    contacts.append(name)
        
        # 返回去重过后的群聊
        return list(set(contacts))
    
    # 检测微信是否收到新消息
    def check_new_msg(self):
        self.open_wechat()
        self.get_wechat()
        
        # 获取左侧聊天按钮
        chat_btn = auto.ButtonControl(Name=self.lc.chats)
        double_click(chat_btn)
        
        # 持续点击聊天按钮，直到获取完全部新消息
        item = auto.ListItemControl(Depth=10)
        prev_name = item.ButtonControl().Name
        
        while True:
            # 判断该联系人是否有新消息
            pane_control = item.PaneControl()
            if len(pane_control.GetChildren()) == 3:
                print(f"{item.ButtonControl().Name} 有新消息")
                # 判断该联系人是否需要自动回复
                if item.ButtonControl().Name in self.auto_reply_contacts:
                    print(f"自动回复 {item.ButtonControl().Name}")
                    self._auto_reply(item, self.auto_reply_msg)
                
            click(item)
            
            # 跳转到下一个新消息
            double_click(chat_btn)
            item = auto.ListItemControl(Depth=10)
            
            # 已经完成遍历，退出循环
            if prev_name == item.ButtonControl().Name:
                break
            
            prev_name = item.ButtonControl().Name
    
    # 设置自动回复的联系人
    def set_auto_reply(self, contacts):
        # contacts是一个列表
        self.auto_reply_contacts = contacts
    
    # 自动回复
    def _auto_reply(self, element, text):
        click(element)
        pyperclip.copy(text)
        auto.SendKeys("{Ctrl}v")
        self.press_enter()
    
    # 识别聊天内容的类型
    # 0：用户发送    1：时间信息  2：红包信息  3：”查看更多消息“标志 4：撤回消息
    def _detect_type(self, list_item_control: auto.ListItemControl) -> int:
        value = None
        # 判断内容框是否为时间框，如果是时间框则子控件不是PaneControl
        if not isinstance(list_item_control.GetFirstChildControl(), auto.PaneControl):
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
            elif "红包" in list_item_control.Name or "Red packet" in list_item_control.Name:
                value = 2
            # 或者是撤回消息
            elif "撤回了一条消息" in list_item_control.Name:
                value = 4
                
        if value is None:
            raise ValueError("无法识别该控件类型")
        
        return value
    
    # 获取聊天窗口
    def _get_chat_frame(self, name: str):
        self.get_contact(name)
        return auto.ListControl(Name=self.lc.message)
    
    def save_dialog_pictures(self, name: str, num: int, save_dir: str) -> None:
        """
        保存指定聊天记录中的图片。图片的名字代表图片在聊天记录中的顺序，从1开始代表最新的图片。
        Args:
            name: 聊天窗口的名字
            num: 保存的最大数量（从最新图片开始保存）
            save_dir: 保存的目录
        """
        
        # 进入图片聊天记录界面
        self.get_contact(name)
        click(auto.ButtonControl(Name=self.lc.chat_history, Depth=14))
        click(auto.TabItemControl(Name=self.lc.photos_n_videos, Depth=6))
        
        # 图片栏控件
        list_control = auto.ListControl(Name=self.lc.photos_n_videos, Depth=6)
        
        # 如果图片数量 < num，则继续往上翻直到满足条件或无法上翻为止
        move(list_control.GetLastChildControl())
        pictures = set()
        cnt = 0
        while cnt < num:
            ori_cnt = cnt
            for list_item_control in list_control.GetChildren()[::-1]:
                # 如果标签不是图片则跳过
                if len(list_item_control.GetFirstChildControl().GetChildren()) == 3:
                    continue
                
                if cnt < num:
                    # 复制图片到剪切板
                    right_click(list_item_control)
                    menu = auto.ListControl(Depth=4)
                    copy = menu.GetFirstChildControl()
                    # 如果图片已经被清理则跳过
                    if copy.Name != self.lc.copy:
                        continue
                    else:
                        click(auto.MenuItemControl(Name=self.lc.copy, Depth=5))
                    
                    # 获取图片路径防止重复存储
                    pic_hash = ImageGrab.grabclipboard()[0]

                    # 获取后缀
                    suffix = pic_hash.split(".")[-1]
                    
                    # 保存图片
                    if pic_hash not in pictures:
                        cnt += 1
                        pictures.add(pic_hash)
                        save_path = os.path.join(save_dir, f"{cnt}.{suffix}")
                        os.system(f"copy \"{pic_hash}\" \"{save_path}\"")
            # 上滑
            pyautogui.scroll(300)
            # 如果无法上滑则退出
            if ori_cnt == cnt:
                break
            
    # 获取指定聊天窗口的聊天记录
    def get_dialogs(self, name: str, n_msg: int,search_user: bool = True) -> List:
        """
        Args:
            name: 聊天窗口的姓名
            n_msg: 获取聊天记录的最大数量（从最后一条往上算）
            search_user: 是否需要搜索用户

        Return:
            dialogs: 聊天记录列表，内部元素为三元组（信息类型，发送人，发送内容）
        """
        if search_user:
            list_control = self._get_chat_frame(name)
        else:
            list_control = auto.ListControl(Name=self.lc.message)
        scroll_pattern = list_control.GetScrollPattern()

        # 如果聊天记录数量 < n_msg，则继续往上翻直到满足条件或无法上翻为止
        while len(list_control.GetChildren()) < n_msg:
            # 如果滑轮存在，将聊天记录翻到“查看更多消息”
            if scroll_pattern:
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
        value_to_info = {0: '用户发送', 1: '时间信息', 2: '红包信息', 3: '"查看更多消息"标志', 4: '撤回消息', 5: "System Notification"}
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
    # # 测试
    path = "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    # path = "D:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    wechat = WeChat(path, locale="zh-CN")
    
    wechat.get_contact("文件")
    
    # groups = wechat.find_all_groups()
    # print(groups)
    # print(len(groups))
    #
    # # wechat.send_msg(name, msg)
    # logs = wechat.get_dialogs(name, 50)
    # print(logs)
    
    
    