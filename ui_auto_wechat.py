import time
import uiautomation as auto
import subprocess
import numpy as np
import pyperclip
import os
import pyautogui
import qianfan
import json
import random

from PIL import ImageGrab
from clipboard import setClipboardFiles
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl
from typing import List


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
    def __init__(self, path):
        # 微信打开路径
        self.path = path
        
        # 用于复制内容到剪切板
        self.app = QApplication([])
        
        # 自动回复的联系人列表
        self.auto_reply_contacts = []
        
        # 自动回复的内容
        self.auto_reply_msg = ["唉", "我也觉得是", "确实是这样", "这倒是真的", "不会吧", "卧槽", "那确实", "没毛病", "嗯嗯", "哎"]

        self.chat_comp = qianfan.ChatCompletion()

        self.retard_list = []
        
    # 打开微信客户端
    def open_wechat(self):
        subprocess.Popen(self.path)
    
    # 搜寻微信客户端控件
    def get_wechat(self):
        return auto.WindowControl(Depth=1, Name="微信")
    
    # 搜索指定用户
    def get_contact(self, name):
        self.open_wechat()
        self.get_wechat()
        
        search_box = auto.EditControl(Depth=8, Name="搜索")
        click(search_box)
        
        pyperclip.copy(name)
        auto.SendKeys("{Ctrl}v")
        # 等待客户端搜索联系人
        time.sleep(0.1)
        search_box.SendKeys("{enter}")
    
    # 鼠标移动到发送按钮处点击发送消息
    def set_retard_list(self, retard_list):
        self.retard_list = retard_list
    
    def press_enter(self):
        # 获取发送按钮
        send_button = auto.ButtonControl(Depth=15, Name="发送(S)")
        click(send_button)
    
    # 在指定群聊中@他人（若@所有人需具备@所有人权限）
    def at(self, name, at_name):
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
    
    # 搜索指定用户名的联系人发送信息
    def send_msg(self, name, text):
        self.get_contact(name)
        pyperclip.copy(text)
        auto.SendKeys("{Ctrl}v")
        self.press_enter()
    
    # 搜索指定用户名的联系人发送文件
    def send_file(self, name: str, path: str):
        """
        Args:
            name: 指定用户名的名称，输入搜索框后出现的第一个人
            path: 发送文件的本地地址
        """
        
        # 粘贴文件发送给用户
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
    
    # 检测微信是否收到新消息
    def check_new_msg(self):
        self.open_wechat()
        self.get_wechat()
        
        # 获取左侧聊天按钮
        chat_btn = auto.ButtonControl(Name="聊天")
        double_click(chat_btn)
        
        # 持续点击聊天按钮，直到获取完全部新消息
        item = auto.ListItemControl(Depth=10)
        prev_name = item.ButtonControl().Name
        
        while True:
            # 判断该联系人是否有新消息
            pane_control = item.PaneControl()
            temp = pane_control.GetChildren()
            if len(temp) == 3:
                print(f"{item.ButtonControl().Name} 有新消息")
                
                # 判断该联系人是否需要自动回复
                if item.ButtonControl().Name in self.auto_reply_contacts:
                    dialogs = self.get_dialogs(item.ButtonControl().Name, 1)[0]
                    resp = ""
                    if dialogs[0] == "撤回消息" or dialogs[2].startswith( '[' ):
                        print("触发了无法识别的消息类型，自动回复哈哈哈")
                        resp = '哈哈哈哈哈'
                        self._auto_reply(item, resp)
                    elif prev_name in self.retard_list:
                        print("恼蚕群回点弱智内容就行")
                        resp = self.auto_reply_msg[random.randint(0, len(self.auto_reply_msg) - 1)]
                        self._auto_reply(item, resp)
                    else:
                        print("调用了千帆来认真的敷衍")
                        resp = self.get_result(dialogs[2])["msg"]
                        self._auto_reply(item, resp)
                    print(f"自动回复 {item.ButtonControl().Name} : {resp}")
                    time.sleep(5)

            click(item)
        
            # 跳转到下一个新消息
            double_click(chat_btn)
            item = auto.ListItemControl(Depth=10)
            
            # 已经完成遍历，退出循环
            # if prev_name == item.ButtonControl().Name:
            #     break
            
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
            elif "红包" in list_item_control.Name:
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
        return auto.ListControl(Name="消息")
    
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
        click(auto.ButtonControl(Name="聊天记录", Depth=14))
        click(auto.TabItemControl(Name="图片与视频", Depth=6))
        
        # 图片栏控件
        list_control = auto.ListControl(Name="图片与视频", Depth=6)
        
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
                    if copy.Name != "复制":
                        continue
                    else:
                        click(auto.MenuItemControl(Name="复制", Depth=5))
                    
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
        value_to_info = {0: '用户发送', 1: '时间信息', 2: '红包信息', 3: '"查看更多消息"标志', 4: '撤回消息'}
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



    #从qianfan大模型中获取回复，用于自动回复
    def get_result(self, str) -> dict:
        prompt = "你是一个聊天助手，我会给你一个消息，你需要对这个消息做出回复，回复的规则如下，你需要严格遵守这个规则，不能回复我给定词之外的其他词语：\
        如果言语具有攻击性，你只能回复：“别急”或者劝他人冷静的话，但是必须包含别急，\
        如果言语只是单纯表达观点，或陈述观点，你只能回复诸如：“这倒是真的”，“确实”，“没错”等无意义的附和消息，一定不要回复任何有意义的话语，\
        如果言语意义不明，你只能回复：“老馋吗”\
        如果内容令人感到不适，你要回复：“好恶心”；\
        如果言语包含赞美或喜爱的情绪，你只能回复：“嘻嘻”或着“么么”等表达喜爱的话语\
        如果消息是一个问题，如果这个问题是选择性的，你可以尝试回答；如果这是一个开放性的问题，你只能回复：“不知道”\
        你的回复不能超过20个字。\
        你需要返回给我一个json格式的代码，这个json代码一定要包含\"msg\"字段，\"msg\"字段中包含着你的回复。\
        且json代码中不能包含换行符号（即\\n符号）以及代码块（即```符号），否则你的回复无效\
        消息如下："
        
        input = prompt + str
        resp = self.chat_comp.do(model="XuanYuan-70B-Chat-4bit", messages=[{
            "role": "user",
            "content": input
        }])
        response = resp["body"]["result"]
        response = response[1:-4]
        try:
            result = json.loads(response)
        except :
            print("json解析失败，回复颜文字")
            result = {"msg": "Σ(°ロ°)"}
        return result



    # wechat.send_msg(name, text)
    # wechat.send_file(name, file)
    
    # contacts = wechat.find_all_contacts()
    # print(len(contacts))
    
    # res = wechat.get_dialogs("easychat", 100)
    # for i in res:
    #     print(i)
    
    # wechat.save_dialog_pictures("xx", 15, "C:/Users/LTEnj/Desktop/")