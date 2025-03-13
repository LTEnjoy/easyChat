import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

class MessageSenderThread(QThread):
    """
    消息发送线程类，用于在后台线程中处理消息发送。避免因阻塞GUI线程导致程序无响应。
    """
    # 定义信号
    message_sent = pyqtSignal(int)  # 发送消息后的信号，参数为当前消息索引
    sending_finished = pyqtSignal()  # 发送完成的信号
    sending_error = pyqtSignal(str)  # 发送错误的信号，参数为错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interval = 0  # 发送间隔时间（秒）
        self.contacts_view = None  # 联系人列表
        self.msg = None  # 消息列表
        self.wechat = None  # 微信操作对象
        self.hotkey_pressed = False  # 热键是否被按下
        
        # 发送范围
        self.start_index = 0
        self.end_index = 0
        
        # 是否停止发送
        self.is_stopped = False
    
    def setup(self, wechat, contacts_view, msg, interval, start_index=None, end_index=None):
        """
        设置发送参数
        """
        self.wechat = wechat
        self.contacts_view = contacts_view
        self.msg = msg
        self.interval = interval
        
        # 如果未定义范围的开头和结尾，则默认发送全部信息
        if start_index is None:
            self.start_index = 0
        else:
            self.start_index = start_index - 1  # 转为0索引
            
        if end_index is None:
            self.end_index = self.msg.count() - 1
        else:
            self.end_index = end_index - 1  # 转为0索引
        
        self.is_stopped = False
        self.hotkey_pressed = False
    
    def stop(self):
        """
        停止发送
        """
        self.is_stopped = True
    
    def set_hotkey_pressed(self, pressed):
        """
        设置热键是否被按下
        """
        self.hotkey_pressed = pressed
        QMessageBox.warning(self, "发送失败", f"因热键按下，已停止发送！")
    
    def run(self):
        try:
            # 获得用户编号列表
            for user_i in range(self.contacts_view.count()):
                if self.is_stopped or self.hotkey_pressed:
                    break
                    
                rank, name = self.contacts_view.item(user_i).text().split(':', 1)
                # For the first message, we need to search user
                search_user = True
                
                for msg_i in range(self.start_index, self.end_index + 1):
                    if self.is_stopped or self.hotkey_pressed:
                        break
                        
                    # 等待间隔时间（在线程中等待不会阻塞GUI）
                    if msg_i > self.start_index:  # 第一条消息不需要等待
                        time.sleep(int(self.interval))
                    
                    msg = self.msg.item(msg_i).text().replace("\\n", "\n")
                    
                    _, type, to, content = msg.split(':', 3)
                    # 判断是否需要发送给该用户
                    if to == "all" or str(rank) in to.split(','):
                        # 判断为文本内容
                        if type == "text":
                            self.wechat.send_msg(name, content, search_user)
                        
                        # 判断为文件内容
                        elif type == "file":
                            self.wechat.send_file(name, content, search_user)
                        
                        # 判断为@他人
                        elif type == "at":
                            self.wechat.at(name, content, search_user)
                    
                        # 搜索用户只在第一次发送时进行
                        search_user = False
                    
                    # 发送消息后发出信号
                    self.message_sent.emit(msg_i)
            
            # 发送完成后发出信号
            self.sending_finished.emit()
            
        except Exception as e:
            import traceback
            error_msg = f"发送失败！请检查内容格式或是否有遗漏步骤！\n错误信息：{e}\n\n堆栈跟踪信息：\n{traceback.format_exc()}"
            self.sending_error.emit(error_msg)