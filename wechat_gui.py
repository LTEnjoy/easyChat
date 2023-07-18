import sys
import time


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui_auto_wechat import WeChat
from functools import partial


# 定时发送子线程类
class ClockThread(QThread):
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

            for i in range(self.clocks.count()):
                clock_hour, clock_min, st_ed = self.clocks.item(i).text().split(" ")
                st, ed = st_ed.split('-')
                if int(clock_hour) == hour and int(clock_min) == min:
                    self.send_func(st=int(st), ed=int(ed))
                    # self.send_func()
            time.sleep(60)


class MyListWidget(QListWidget):
    """支持双击可编辑的QListWidget"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 设置选择多个

        # 双击可编辑
        self.edited_item = self.currentItem()
        self.close_flag = True
        self.doubleClicked.connect(self.item_double_clicked)
        self.currentItemChanged.connect(self.close_edit)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        """回车事件，关闭edit"""
        super().keyPressEvent(e)
        if e.key() == Qt.Key_Return:
            if self.close_flag:
                self.close_edit()
            self.close_flag = True

    def edit_new_item(self) -> None:
        """edit一个新的item"""
        self.close_flag = False
        self.close_edit()
        count = self.count()
        self.addItem('')
        item = self.item(count)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)

    def item_double_clicked(self, modelindex: QModelIndex) -> None:
        """双击事件"""
        self.close_edit()
        item = self.item(modelindex.row())
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)

    def close_edit(self, *_) -> None:
        """关闭edit"""
        if self.edited_item and self.isPersistentEditorOpen(self.edited_item):
            self.closePersistentEditor(self.edited_item)


class WechatGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.wechat = WeChat(None)
        self.clock = ClockThread()

        # 发消息的用户列表
        self.contacts = []

        # 初始化图形界面
        self.initUI()

    # 选择用户界面的初始化
    def init_choose_contacts(self):
        # 读取联系人列表并保存
        def save_contacts():
            path = QFileDialog.getSaveFileName(self, "保存联系人列表", "contacts.txt", "文本文件(*.txt)")[0]
            if not path == "":
                contacts = self.wechat.find_all_contacts()
                with open(path, 'w', encoding='utf-8') as f:
                    for contact in contacts:
                        f.write(contact + '\n')
                
                QMessageBox.information(self, "保存成功", "联系人列表保存成功！")
        
        # 读取联系人列表并加载
        def load_contacts():
            path = QFileDialog.getOpenFileName(self, "加载联系人列表", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.contacts_view.addItem(line.strip())
                
                QMessageBox.information(self, "加载成功", "联系人列表加载成功！")
        
        # 增加用户列表信息
        def add_contact():
            name_list, ok = QInputDialog.getText(self, '添加用户', '输入添加的用户名(可添加多个人名，用英文逗号,分隔):')
            if ok:
                if name_list != "":
                    names = name_list.split(',')
                    for name in names:
                        self.contacts_view.addItem(str(name).strip())

        # 删除用户信息
        def del_contact():
            for i in range(self.contacts_view.count()-1, -1, -1):
                if self.contacts_view.item(i).isSelected():
                    self.contacts_view.takeItem(i)

        hbox = QHBoxLayout()

        # 左边的用户列表
        self.contacts_view = MyListWidget()
        self.clock.contacts = self.contacts_view
        for name in self.contacts:
            self.contacts_view.addItem(name)

        hbox.addWidget(self.contacts_view)

        # 右边的按钮界面
        vbox = QVBoxLayout()
        vbox.stretch(1)
        
        # 用户界面的按钮
        info = QLabel("待发送用户列表")
        
        save_btn = QPushButton("保存微信好友列表")
        save_btn.clicked.connect(save_contacts)
        
        load_btn = QPushButton("加载用户txt文件")
        load_btn.clicked.connect(load_contacts)
        
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(add_contact)
        
        del_btn = QPushButton("删除用户")
        del_btn.clicked.connect(del_contact)

        vbox.addWidget(info)
        vbox.addWidget(save_btn)
        vbox.addWidget(load_btn)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        hbox.addLayout(vbox)

        return hbox

    # 定时功能界面的初始化
    def init_clock(self):
        # 按钮响应：增加时间
        def add_contact():
            name, ok = QInputDialog.getText(self, '添加时间', "输入格式:'小时(0~23) 分钟(0~59) 发送信息的范围 (xx-xx) '，\n"
                                                          "例 12 35 1-10 为12:35发送内容栏的第1条至第10条")
            if ok:
                if name != "":
                    self.time_view.addItem(str(name))

        # 按钮响应：删除时间
        def del_contact():
            for i in range(self.time_view.count() - 1, -1, -1):
                if self.time_view.item(i).isSelected():
                    self.time_view.takeItem(i)

        # 按钮响应：开始定时
        def start_counting():
            if self.clock.time_counting is True:
                return
            else:
                self.clock.time_counting = True

            info.setStyleSheet("color:red")
            info.setText("定时发送（目前已开始）")
            self.clock.start()

        # 按钮响应：结束定时
        def end_counting():
            self.clock.time_counting = False
            info.setStyleSheet("color:black")
            info.setText("定时发送（目前未开始）")

        hbox = QHBoxLayout()

        # 左边的用户列表
        self.time_view = MyListWidget()
        self.clock.clocks = self.time_view
        hbox.addWidget(self.time_view)

        # 右边的按钮界面
        vbox = QVBoxLayout()
        vbox.stretch(1)

        info = QLabel("定时发送（目前未开始）")
        add_btn = QPushButton("添加时间")
        add_btn.clicked.connect(add_contact)
        del_btn = QPushButton("删除时间")
        del_btn.clicked.connect(del_contact)
        start_btn = QPushButton("开始定时")
        start_btn.clicked.connect(start_counting)
        end_btn = QPushButton("结束定时")
        end_btn.clicked.connect(end_counting)

        vbox.addWidget(info)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        vbox.addWidget(start_btn)
        vbox.addWidget(end_btn)
        hbox.addLayout(vbox)

        return hbox

    # 发送消息内容界面的初始化
    def init_send_msg(self):
        # 增加一条文本信息
        def add_text():
            name, ok = QInputDialog.getText(self, '添加文本内容', '输入添加的内容:')
            rank_str = f"{self.msg.count() + 1}:"
            if ok:
                if name != "":
                    # 判断给文本是否是@信息
                    if name[:3] == "at:":
                        self.msg.addItem(rank_str+str(name))
                    else:
                        self.msg.addItem(rank_str+f"text:{str(name)}")

        # 增加一个文件
        def add_file():
            path = QFileDialog.getOpenFileName(self, '打开文件', '/home')[0]
            rank_str = f"{self.msg.count() + 1}:"
            if path != "":
                self.msg.addItem(rank_str+f"file:{str(path)}")

        # 删除一条发送的信息
        def del_content():
            for i in range(self.msg.count() - 1, -1, -1):
                if self.msg.item(i).isSelected():
                    self.msg.takeItem(i)

        # 发送按钮响应事件
        def send_msg(gap=None, st=None, ed=None):
            # 如果未定义范围的开头和结尾，则默认发送全部信息
            if st is None:
                st = 1
                ed = self.msg.count()

            for user_i in range(self.contacts_view.count()):
                name = self.contacts_view.item(user_i).text()

                for msg_i in range(st-1, ed):
                    msg = self.msg.item(msg_i).text()

                    _, type, content = msg.split(':', 2)

                    # 判断为文本内容
                    if type == "text":
                        self.wechat.send_msg(name, content)

                    # 判断为文件内容
                    elif type == "file":
                        self.wechat.send_file(name, content)

                    # 判断为@他人
                    elif type == "at":
                        self.wechat.at(name, content)

        # 左边的布局
        vbox_left = QVBoxLayout()

        # 提示信息
        info = QLabel("添加要发送的内容（程序将按顺序发送）")

        # 输入内容框
        self.msg = MyListWidget()
        self.clock.send_func = send_msg

        # 发送按钮
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(send_msg)

        vbox_left.addWidget(info)
        vbox_left.addWidget(self.msg)
        vbox_left.addWidget(send_btn)

        # 右边的选择内容界面
        vbox_right = QVBoxLayout()
        vbox_right.stretch(1)

        text_btn = QPushButton("添加文本内容")
        text_btn.clicked.connect(add_text)

        file_btn = QPushButton("添加文件")
        file_btn.clicked.connect(add_file)

        del_btn = QPushButton("删除内容")
        del_btn.clicked.connect(del_content)

        vbox_right.addWidget(text_btn)
        vbox_right.addWidget(file_btn)
        vbox_right.addWidget(del_btn)

        # 整体布局
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        return hbox

    def initUI(self):
        # 垂直布局
        vbox = QVBoxLayout()

        # 显示微信exe路径
        self.path_label = QLabel("", self)
        self.path_label.setWordWrap(True)
        # self.path_label.resize(self.width(), 100)

        # 选择微信exe路径的按钮
        self.path_btn = QPushButton("选择微信打开路径", self)
        self.path_btn.resize(self.path_btn.sizeHint())
        self.path_btn.clicked.connect(self.choose_path)

        # self.open_wechat_btn = QPushButton("打开微信", self)
        # self.open_wechat_btn.clicked.connect(self.open_wechat)

        # 用户选择界面
        contacts = self.init_choose_contacts()

        # 发送内容界面
        msg_widget = self.init_send_msg()

        # 定时界面
        clock = self.init_clock()

        vbox.addWidget(self.path_label)
        vbox.addWidget(self.path_btn)
        vbox.addLayout(contacts)
        vbox.addStretch(5)
        vbox.addLayout(msg_widget)
        vbox.addStretch(5)
        vbox.addLayout(clock)
        vbox.addStretch(1)

        # qle.textChanged[str].connect(self.onChanged)

        self.setLayout(vbox)
        self.setFixedSize(500, 700)
        self.setWindowTitle('EasyChat微信助手')
        self.show()

    # 选择微信exe路径
    def choose_path(self):
        path = QFileDialog.getOpenFileName(self, '打开文件', '/home')[0]
        if path != "":
            self.path_label.setText(path)
            self.wechat.path = path

    # 打开微信
    def open_wechat(self):
        self.wechat.open_wechat()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WechatGUI()
    sys.exit(app.exec_())