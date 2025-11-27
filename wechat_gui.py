import sys
import time
import os
import itertools
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from ui_auto_wechat import WeChat
from ui_auto_wechat import WeChat
from module import *
from wechat_locale import WeChatLocale


class WechatGUI(QWidget):

    def __init__(self):
        super().__init__()

        # 读取之前保存的配置文件，如果没有则新建一个
        self.config_path = "wechat_config.json"
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as r:
                self.config = json.load(r)

        else:
            # 默认配置
            self.config = {
                "settings": {
                    "wechat_path": "",
                    "send_interval": 0,
                    "system_version": "new",
                    "language": "zh-CN",
                },
                "contacts": [],
                "messages": [],
                "schedules": [],
            }
            self.save_config()

        self.wechat = WeChat(
            path=self.config["settings"]["wechat_path"],
            locale=self.config["settings"]["language"],
        )
        self.clock = ClockThread()

        # 发消息的用户列表
        self.contacts = []

        # 初始化图形界面
        self.initUI()

        # 判断全局热键是否被按下
        self.hotkey_pressed = False
        keyboard.add_hotkey('ctrl+alt', self.hotkey_press)

    # 保存当前的配置
    def save_config(self):
        with open(self.config_path, "w", encoding="utf8") as w:
            json.dump(self.config, w, indent=4, ensure_ascii=False)

    def hotkey_press(self):
        print("hotkey pressed")
        self.hotkey_pressed = True

    # 选择用户界面的初始化
    def init_choose_contacts(self):
        # 在联系人有变化后更新配置文件
        def update_contacts():
            contacts = []
            for i in range(self.contacts_view.count()):
                contacts.append(self.contacts_view.item(i).text())

            self.config["contacts"] = contacts
            self.save_config()

        # 读取联系人列表并保存
        def save_contacts():
            # 弹出错误框提醒该功能暂未适配新版微信
            QMessageBox.warning(self, "功能未适配", "该功能暂未适配新版微信，敬请期待！")

            # path = QFileDialog.getSaveFileName(self, "保存联系人列表", "contacts.csv", "表格文件(*.csv)")[0]
            # if not path == "":
            #     contacts = self.wechat.find_all_contacts()
            #     contacts.to_csv(path, index=False, encoding='utf_8_sig')
            #     # with open(path, 'w', encoding='utf-8') as f:
            #     #     for contact in contacts:
            #     #         f.write(contact + '\n')
            #
            #     QMessageBox.information(self, "保存成功", "联系人列表保存成功！")

        # 保存群聊列表
        def save_groups():
            QMessageBox.warning(self, "功能未适配", "该功能暂未适配新版微信，敬请期待！")
            # path = QFileDialog.getSaveFileName(self, "保存群聊列表", "groups.txt", "文本文件(*.txt)")[0]
            # if not path == "":
            #     contacts = self.wechat.find_all_groups()
            #     with open(path, 'w', encoding='utf-8') as f:
            #         for contact in contacts:
            #             f.write(contact + '\n')
            #
            #     QMessageBox.information(self, "保存成功", "群聊列表保存成功！")

        # 读取联系人列表并加载
        def load_contacts():
            path = QFileDialog.getOpenFileName(self, "加载联系人列表", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.contacts_view.addItem(f"{self.contacts_view.count()+1}:{line.strip()}")

                update_contacts()
                QMessageBox.information(self, "加载成功", "联系人列表加载成功！")

        # 增加用户列表信息
        def add_contact():
            name_list, ok = QInputDialog.getText(self, '添加用户', '输入添加的用户名(可添加多个人名，用英文逗号,分隔):')
            if ok:
                if name_list != "":
                    names = name_list.split(',')
                    for name in names:
                        id = f"{self.contacts_view.count() + 1}"
                        self.contacts_view.addItem(f"{id}:{str(name).strip()}")
                    update_contacts()

        # 删除用户信息
        def del_contact():
            # 删除选中的用户
            for i in range(self.contacts_view.count()-1, -1, -1):
                if self.contacts_view.item(i).isSelected():
                    self.contacts_view.takeItem(i)

            # 为所有剩余的用户重新编号
            for i in range(self.contacts_view.count()):
                self.contacts_view.item(i).setText(f"{i+1}:{self.contacts_view.item(i).text().split(':')[1]}")

            update_contacts()

        hbox = QHBoxLayout()

        # 左边的用户列表
        self.contacts_view = MyListWidget()

        # 加载配置文件里保存的用户
        for contact in self.config["contacts"]:
            self.contacts_view.addItem(contact)

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

        save_group_btn = QPushButton("保存微信群聊列表")
        save_group_btn.clicked.connect(save_groups)

        load_btn = QPushButton("加载用户txt文件")
        load_btn.clicked.connect(load_contacts)

        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(add_contact)

        del_btn = QPushButton("删除用户")
        del_btn.clicked.connect(del_contact)

        vbox.addWidget(info)
        vbox.addWidget(save_btn)
        vbox.addWidget(save_group_btn)
        vbox.addWidget(load_btn)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        hbox.addLayout(vbox)

        return hbox

    # 定时功能界面的初始化
    def init_clock(self):
        # 在定时列表有变化后更新配置文件
        def update_schedules():
            schedules = []
            for i in range(self.time_view.count()):
                schedules.append(self.time_view.item(i).text())

            self.config["schedules"] = schedules
            self.save_config()
            
        # 按钮响应：增加时间
        def add_contact():
            inputs = [
                "注：在每一个时间输入框内都可以使用英文逗号“,“来一次性区分多个数值进行多次定时。\n(例：分钟框输入 10,20,30,40)",
                "月 (1~12)",
                "日 (1~31)",
                "小时（0~23）",
                "分钟 (0~59)",
                "发送信息的起点（从哪一条开始发）",
                "发送信息的终点（到哪一条结束，包括该条）",
            ]

            # 设置默认值为当前时间
            local_time = time.localtime(time.time())
            default_values = [
                str(local_time.tm_year),
                str(local_time.tm_mon),
                str(local_time.tm_mday),
                str(local_time.tm_hour),
                str(local_time.tm_min),
                "",
                "",
            ]

            dialog = MultiInputDialog(inputs, default_values)
            if dialog.exec_() == QDialog.Accepted:
                year, month, day, hour, min, st, ed = dialog.get_input()
                if year == "" or month == "" or day == "" or hour == "" or min == "" or st == "" or ed == "":
                    QMessageBox.warning(self, "输入错误", "输入不能为空！")
                    return

                else:
                    year_list = [y.strip() for y in year.split(',')]
                    month_list = [m.strip() for m in month.split(',')]
                    day_list = [d.strip() for d in day.split(',')]
                    hour_list = [h.strip() for h in hour.split(',')]
                    min_list = [m.strip() for m in min.split(',')]

                    for year, month, day, hour, min in itertools.product(year_list, month_list, day_list, hour_list, min_list):
                        input = f"{year} {month} {day} {hour} {min} {st}-{ed}"
                        self.time_view.addItem(input)
                    
                    update_schedules()

        # 按钮响应：删除时间
        def del_contact():
            for i in range(self.time_view.count() - 1, -1, -1):
                if self.time_view.item(i).isSelected():
                    self.time_view.takeItem(i)
            
            update_schedules()

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

        # 按钮相应：开启防止自动下线。开启后每隔一小时自动点击微信窗口，防止自动下线
        def prevent_offline():
            if self.clock.prevent_offline is True:
                self.clock.prevent_offline = False
                prevent_btn.setStyleSheet("color:black")
                prevent_btn.setText("防止自动下线：（目前关闭）")

            else:
                # 弹出提示框
                QMessageBox.information(self, "防止自动下线", "防止自动下线已开启！每隔一小时自动点击微信窗口，防"
                                                              "止自动下线。请不要在正常使用电脑时使用该策略。")

                self.clock.prevent_offline = True
                prevent_btn.setStyleSheet("color:red")
                prevent_btn.setText("防止自动下线：（目前开启）")

        hbox = QHBoxLayout()

        # 左边的时间列表
        self.time_view = MyListWidget()
        # 加载配置文件里保存的用户
        for schedule in self.config["schedules"]:
            self.time_view.addItem(schedule)
            
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
        prevent_btn = QPushButton("防止自动下线：（目前关闭）")
        prevent_btn.clicked.connect(prevent_offline)

        vbox.addWidget(info)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        vbox.addWidget(start_btn)
        vbox.addWidget(end_btn)
        vbox.addWidget(prevent_btn)
        hbox.addLayout(vbox)

        return hbox

    # 发送消息内容界面的初始化
    def init_send_msg(self):
        # 在发送消息有变化后更新配置文件
        def update_messages():
            messages = []
            for i in range(self.msg.count()):
                messages.append(self.msg.item(i).text())

            self.config["messages"] = messages
            self.save_config()

        # 从txt中加载消息内容
        def load_text():
            path = QFileDialog.getOpenFileName(self, "加载内容文本", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.msg.addItem(f"{self.msg.count()+1}:text:{line.strip()}")

                QMessageBox.information(self, "加载成功", "内容文本加载成功！")

        # 增加一条文本信息
        def add_text():
            inputs = [
                "是否需要at他人(无则不填，有则填写所有你要at的人名，用英文逗号分隔。要at所有人就填写'所有人')",
                "请输入发送的文本内容(如果需要换行则输入\\n，例如你好\\n吃饭了吗？)",
                "请指定发送给哪些用户(1,2,3代表发送给前三位用户)，如需全部发送请忽略此项",
            ]
            dialog = MultiInputDialog(inputs)
            if dialog.exec_() == QDialog.Accepted:
                at, text, to = dialog.get_input()
                to = "all" if to == "" else to
                if text != "":
                    # 消息的序号
                    rank = self.msg.count() + 1

                    self.msg.addItem(f"{rank}:text:{to}:{at}:{str(text)}")
                    update_messages()

        # 增加一个文件
        def add_file():
            dialog = FileDialog()
            if dialog.exec_() == QDialog.Accepted:
                to, path = dialog.get_input()
                to = "all" if to == "" else to
                if path != "":
                    self.msg.addItem(f"{self.msg.count()+1}:file:{to}:{str(path)}")
                    update_messages()

        # 删除一条发送的信息
        def del_content():
            # 删除选中的信息
            for i in range(self.msg.count() - 1, -1, -1):
                if self.msg.item(i).isSelected():
                    self.msg.takeItem(i)

            # 为所有剩余的信息重新设置编号
            for i in range(self.msg.count()):
                self.msg.item(i).setText(f"{i+1}:"+self.msg.item(i).text().split(':', 1)[1])

            update_messages()

        # 发送按钮响应事件
        def send_msg(gap=None, st=None, ed=None):
            # 在每次发送时进行初始化
            self.hotkey_pressed = False

            # 获取发送间隔
            interval = send_interval.spin_box.value()

            try:
                # 如果未定义范围的开头和结尾，则默认发送全部信息
                if st is None:
                    st = 1
                    ed = self.msg.count()

                # 获得用户编号列表
                for user_i in range(self.contacts_view.count()):
                    # 等待间隔时间
                    time.sleep(int(interval))

                    rank, name = self.contacts_view.item(user_i).text().split(':', 1)
                    # For the first message, we need to search user
                    search_user = True

                    for msg_i in range(st - 1, ed):
                        # 如果全局热键被按下，则停止发送
                        if self.hotkey_pressed is True:
                            QMessageBox.warning(self, "发送失败", f"热键已按下，已停止发送！")
                            return

                        msg = self.msg.item(msg_i).text().replace("\\n", "\n")

                        _, type, to, content = msg.split(':', 3)
                        # 判断是否需要发送给该用户
                        if to == "all" or str(rank) in to.split(','):
                            # 判断为文本内容
                            if type == "text":
                                # 分出at的人和发送的文本内容
                                at_names, text = content.split(":", 1)
                                at_names = at_names.split(",")
                                self.wechat.send_msg(name, at_names, text, search_user)

                            # 判断为文件内容
                            elif type == "file":
                                self.wechat.send_file(name, content, search_user)

                            # 搜索用户只在第一次发送时进行
                            search_user = False

            except Exception as e:
                QMessageBox.warning(self, "发送失败", f"发送失败！请检查内容格式或是否有遗漏步骤！\n错误信息：{e}")
                return

        # 左边的布局
        vbox_left = QVBoxLayout()

        # 提示信息
        info = QLabel("添加要发送的内容（程序将按顺序发送）")

        # 输入内容框
        self.msg = MyListWidget()
        # 加载配置文件里保存的内容
        for message in self.config["messages"]:
            self.msg.addItem(message)

        self.clock.send_func = send_msg
        self.clock.prevent_func = self.wechat.prevent_offline

        # 发送按钮
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(send_msg)

        # 发送不同用户时的间隔
        send_interval = MySpinBox("发送不同用户时的间隔（秒）")
        send_interval.spin_box.setValue(self.config["settings"]["send_interval"])

        # 添加修改间隔的响应
        def change_spin_box():
            interval = send_interval.spin_box.value()
            self.config["settings"]["send_interval"] = interval
            self.save_config()

        send_interval.spin_box.valueChanged.connect(change_spin_box)

        vbox_left.addWidget(info)
        vbox_left.addWidget(self.msg)
        vbox_left.addWidget(send_interval)
        vbox_left.addWidget(send_btn)

        # 右边的选择内容界面
        vbox_right = QVBoxLayout()
        vbox_right.stretch(1)


        load_btn = QPushButton("加载内容txt文件")
        load_btn.clicked.connect(load_text)

        text_btn = QPushButton("添加文本内容")
        text_btn.clicked.connect(add_text)

        file_btn = QPushButton("添加文件")
        file_btn.clicked.connect(add_file)

        del_btn = QPushButton("删除内容")
        del_btn.clicked.connect(del_content)

        vbox_right.addWidget(text_btn)
        vbox_right.addWidget(file_btn)
        vbox_right.addWidget(del_btn)
        vbox_right.addWidget(load_btn)

        # 整体布局
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        return hbox

    # 提供选择微信语言版本的按钮
    def init_language_choose(self):
        def switch_language():
            if lang_zh_CN_btn.isChecked():
                self.wechat.lc = WeChatLocale("zh-CN")
                self.config["settings"]["language"] = "zh-CN"

            elif lang_zh_TW_btn.isChecked():
                self.wechat.lc = WeChatLocale("zh-TW")
                self.config["settings"]["language"] = "zh-TW"

            elif lang_en_btn.isChecked():
                self.wechat.lc = WeChatLocale("en-US")
                self.config["settings"]["language"] = "en-US"

            self.save_config()

        # 提示信息
        info = QLabel("请选择你的微信系统语言")

        # 选择按钮
        lang_zh_CN_btn = QRadioButton("简体中文")
        lang_zh_TW_btn = QRadioButton("繁体中文")
        lang_en_btn = QRadioButton("English")

        if self.config["settings"]["language"] == "zh-CN":
            lang_zh_CN_btn.setChecked(True)

        elif self.config["settings"]["language"] == "zh-TW":
            lang_zh_TW_btn.setChecked(True)

        elif self.config["settings"]["language"] == "en-US":
            lang_en_btn.setChecked(True)

        # 选择按钮的响应事件
        lang_zh_CN_btn.clicked.connect(switch_language)
        lang_zh_TW_btn.clicked.connect(switch_language)
        lang_en_btn.clicked.connect(switch_language)

        # 整体布局
        hbox = QHBoxLayout()
        hbox.addWidget(lang_zh_CN_btn)
        hbox.addWidget(lang_zh_TW_btn)
        hbox.addWidget(lang_en_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(info)
        vbox.addLayout(hbox)

        return vbox

    def initUI(self):
        # 垂直布局
        vbox = QVBoxLayout()

        # 显示微信exe路径
        self.path_label = QLabel(self.config["settings"]["wechat_path"], self)
        self.path_label.setWordWrap(True)
        # self.path_label.resize(self.width(), 100)

        # 选择微信exe路径的按钮
        self.path_btn = QPushButton("选择微信打开路径", self)
        self.path_btn.resize(self.path_btn.sizeHint())
        self.path_btn.clicked.connect(self.choose_path)

        # 选择微信语言界面
        lang = self.init_language_choose()

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
        vbox.addLayout(lang)
        vbox.addLayout(contacts)
        vbox.addStretch(5)
        vbox.addLayout(msg_widget)
        vbox.addStretch(5)
        vbox.addLayout(clock)
        vbox.addStretch(1)

        # qle.textChanged[str].connect(self.onChanged)

        #获取显示器分辨率
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        height = screenRect.height()
        width = screenRect.width()

        self.setLayout(vbox)
        # self.setFixedSize(width*0.2, height*0.6)
        self.setWindowTitle('EasyChat微信助手(作者：LTEnjoy)')
        self.show()

    # 选择微信exe路径
    def choose_path(self):
        path = QFileDialog.getOpenFileName(self, '打开文件', '/home')[0]
        if path != "":
            self.path_label.setText(path)
            self.wechat.path = path

            # 保存到配置文件里
            self.config["settings"]["wechat_path"] = path
            self.save_config()

    # 打开微信
    def open_wechat(self):
        self.wechat.open_wechat()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WechatGUI()
    sys.exit(app.exec_())