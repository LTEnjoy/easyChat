import sys
import time
import itertools

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ui_auto_wechat import WeChat
from module import *
from wechat_locale import WeChatLocale
from style import AppTheme, create_title_label, create_group_box, create_primary_button, create_secondary_button, create_warning_button, create_danger_button
from material_style import apply_material_stylesheet


class WechatGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.wechat = WeChat(None)
        self.clock = ClockThread()

        # 发消息的用户列表
        self.contacts = []

        # 初始化图形界面
        self.initUI()
        
        # 判断全局热键是否被按下
        self.hotkey_pressed = False
        keyboard.add_hotkey('ctrl+alt', self.hotkey_press)
    
    def hotkey_press(self):
        print("hotkey pressed")
        self.hotkey_pressed = True

    # 选择用户界面的初始化
    def init_choose_contacts(self):
        # 读取联系人列表并保存
        def save_contacts():
            path = QFileDialog.getSaveFileName(self, "保存联系人列表", "contacts.csv", "表格文件(*.csv)")[0]
            if not path == "":
                contacts = self.wechat.find_all_contacts()
                contacts.to_csv(path, index=False, encoding='utf_8_sig')
                QMessageBox.information(self, "保存成功", "联系人列表保存成功！")
        
        # 保存群聊列表
        def save_groups():
            path = QFileDialog.getSaveFileName(self, "保存群聊列表", "groups.txt", "文本文件(*.txt)")[0]
            if not path == "":
                contacts = self.wechat.find_all_groups()
                with open(path, 'w', encoding='utf-8') as f:
                    for contact in contacts:
                        f.write(contact + '\n')
                QMessageBox.information(self, "保存成功", "群聊列表保存成功！")
        
        # 读取联系人列表并加载
        def load_contacts():
            path = QFileDialog.getOpenFileName(self, "加载联系人列表", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.contacts_view.addItem(f"{self.contacts_view.count()+1}:{line.strip()}")
                QMessageBox.information(self, "加载成功", "联系人列表加载成功！")
        
        # 增加用户列表信息
        def add_contact():
            name_list, ok = QInputDialog.getText(self, '添加用户', '输入添加的用户名(可添加多个人名，用英文逗号,分隔):')
            if ok and name_list != "":
                names = name_list.split(',')
                for name in names:
                    id = f"{self.contacts_view.count() + 1}"
                    self.contacts_view.addItem(f"{id}:{str(name).strip()}")

        # 删除用户信息
        def del_contact():
            # 删除选中的用户
            for i in range(self.contacts_view.count()-1, -1, -1):
                if self.contacts_view.item(i).isSelected():
                    self.contacts_view.takeItem(i)

            # 为所有剩余的用户重新编号
            for i in range(self.contacts_view.count()):
                self.contacts_view.item(i).setText(f"{i+1}:{self.contacts_view.item(i).text().split(':')[1]}")

        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建标题
        title_label = create_title_label("联系人管理")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建联系人列表区域
        contacts_group = create_group_box("待发送用户列表")
        contacts_layout = QHBoxLayout()
        
        # 左侧联系人列表
        list_layout = QVBoxLayout()
        self.contacts_view = MyListWidget()
        self.clock.contacts = self.contacts_view
        for name in self.contacts:
            self.contacts_view.addItem(name)
        
        # 添加搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_input = QLineEdit()
        search_input.setPlaceholderText("输入关键字筛选联系人")
        search_input.textChanged.connect(lambda text: self.filter_contacts(text))
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        
        list_layout.addLayout(search_layout)
        list_layout.addWidget(self.contacts_view)
        contacts_layout.addLayout(list_layout, 7)
        
        # 右侧按钮区域
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 微信数据操作区
        wechat_data_group = create_group_box("微信数据")
        wechat_data_layout = QVBoxLayout()
        
        save_btn = create_primary_button("保存微信好友列表")
        save_btn.clicked.connect(save_contacts)
        
        save_group_btn = create_primary_button("保存微信群聊列表")
        save_group_btn.clicked.connect(save_groups)
        
        wechat_data_layout.addWidget(save_btn)
        wechat_data_layout.addWidget(save_group_btn)
        wechat_data_group.setLayout(wechat_data_layout)
        
        # 联系人操作区
        contact_actions_group = create_group_box("联系人操作")
        contact_actions_layout = QVBoxLayout()
        
        load_btn = create_secondary_button("加载用户文件")
        load_btn.clicked.connect(load_contacts)
        
        add_btn = create_secondary_button("添加用户")
        add_btn.clicked.connect(add_contact)
        
        del_btn = create_danger_button("删除选中用户")
        del_btn.clicked.connect(del_contact)
        
        contact_actions_layout.addWidget(load_btn)
        contact_actions_layout.addWidget(add_btn)
        contact_actions_layout.addWidget(del_btn)
        contact_actions_group.setLayout(contact_actions_layout)
        
        # 添加到按钮布局
        buttons_layout.addWidget(wechat_data_group)
        buttons_layout.addWidget(contact_actions_group)
        buttons_layout.addStretch()
        
        contacts_layout.addLayout(buttons_layout, 3)
        contacts_group.setLayout(contacts_layout)
        
        main_layout.addWidget(contacts_group)
        
        return main_layout
    
    # 联系人过滤功能
    def filter_contacts(self, text):
        for i in range(self.contacts_view.count()):
            item = self.contacts_view.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    # 定时功能界面的初始化
    def init_clock(self):
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
            if dialog.exec() == QDialog.DialogCode.Accepted:
                year, month, day, hour, min, st, ed = dialog.get_input()
                if year == "" or month == "" or day == "" or hour == "" or min == "" or st == "" or ed == "":
                    QMessageBox.warning(self, "输入错误", "输入不能为空！")
                    return
                
                else:
                    year_list = year.split(',')
                    month_list = month.split(',')
                    day_list = day.split(',')
                    hour_list = hour.split(',')
                    min_list = min.split(',')
                    
                    for year, month, day, hour, min in itertools.product(year_list, month_list, day_list, hour_list, min_list):
                        input = f"{year} {month} {day} {hour} {min} {st}-{ed}"
                        self.time_view.addItem(input)

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

            status_label.setStyleSheet(f"color: {AppTheme.DANGER}; font-weight: bold;")
            status_label.setText("定时发送（目前已开始）")
            self.clock.start()
        
        # 按钮响应：结束定时
        def end_counting():
            self.clock.time_counting = False
            status_label.setStyleSheet(f"color: {AppTheme.TEXT_PRIMARY}; font-weight: normal;")
            status_label.setText("定时发送（目前未开始）")
        
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

        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建标题
        title_label = create_title_label("定时任务管理")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建定时任务区域
        schedule_group = create_group_box("定时任务列表")
        schedule_layout = QHBoxLayout()
        
        # 左侧定时任务列表
        list_layout = QVBoxLayout()
        
        # 状态标签
        status_label = QLabel("定时发送（目前未开始）")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        list_layout.addWidget(status_label)
        
        # 定时任务列表
        self.time_view = MyListWidget()
        self.clock.clocks = self.time_view
        list_layout.addWidget(self.time_view)
        
        schedule_layout.addLayout(list_layout, 7)
        
        # 右侧按钮区域
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 任务操作区
        task_actions_group = create_group_box("任务操作")
        task_actions_layout = QVBoxLayout()
        
        add_btn = create_secondary_button("添加定时任务")
        add_btn.clicked.connect(add_contact)
        
        del_btn = create_danger_button("删除选中任务")
        del_btn.clicked.connect(del_contact)
        
        task_actions_layout.addWidget(add_btn)
        task_actions_layout.addWidget(del_btn)
        task_actions_group.setLayout(task_actions_layout)
        
        # 控制区
        control_group = create_group_box("控制中心")
        control_layout = QVBoxLayout()
        
        start_btn = create_primary_button("开始定时任务")
        start_btn.clicked.connect(start_counting)
        
        end_btn = create_warning_button("停止定时任务")
        end_btn.clicked.connect(end_counting)
        
        control_layout.addWidget(start_btn)
        control_layout.addWidget(end_btn)
        control_group.setLayout(control_layout)
        
        # 添加到按钮布局
        buttons_layout.addWidget(task_actions_group)
        buttons_layout.addWidget(control_group)
        buttons_layout.addStretch()
        
        schedule_layout.addLayout(buttons_layout, 3)
        schedule_group.setLayout(schedule_layout)
        
        main_layout.addWidget(schedule_group)
        
        return main_layout

    # 发送消息内容界面的初始化
    def init_send_msg(self):
        # 从txt中加载消息内容
        def load_text():
            path = QFileDialog.getOpenFileName(self, "加载内容文本", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.msg.addItem(f"{self.msg.count()+1}:text:all:{line.strip()}")
                QMessageBox.information(self, "加载成功", "内容文本加载成功！")

        # 增加一条文本信息
        def add_text():
            inputs = [
                "请输入发送的内容",
                "请指定发送给哪些用户(1,2,3代表发送给前三位用户)，如需全部发送请忽略此项",
            ]
            dialog = MultiInputDialog(inputs)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                text, to = dialog.get_input()
                to = "all" if to == "" else to
                if text != "":
                    # 消息的序号
                    rank = self.msg.count() + 1
                    
                    # 判断给文本是否是@信息
                    if text[:3] == "at:":
                        self.msg.addItem(f"{rank}:at:{to}:{str(text[3:])}")
                    else:
                        self.msg.addItem(f"{rank}:text:{to}:{str(text)}")

        # 增加一个文件
        def add_file():
            dialog = FileDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                to, path = dialog.get_input()
                to = "all" if to == "" else to
                if path != "":
                    self.msg.addItem(f"{self.msg.count()+1}:file:{to}:{str(path)}")

        # 删除一条发送的信息
        def del_content():
            # 删除选中的信息
            for i in range(self.msg.count() - 1, -1, -1):
                if self.msg.item(i).isSelected():
                    self.msg.takeItem(i)

            # 为所有剩余的信息重新设置编号
            for i in range(self.msg.count()):
                self.msg.item(i).setText(f"{i+1}:"+self.msg.item(i).text().split(':', 1)[1])

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
                                self.wechat.send_msg(name, content, search_user)
                            
                            # 判断为文件内容
                            elif type == "file":
                                self.wechat.send_file(name, content, search_user)
                            
                            # 判断为@他人
                            elif type == "at":
                                self.wechat.at(name, content, search_user)
                        
                            # 搜索用户只在第一次发送时进行
                            search_user = False

            except Exception as e:
                import traceback
                error_msg = f"发送失败！请检查内容格式或是否有遗漏步骤！\n错误信息：{e}\n\n堆栈跟踪信息：\n{traceback.format_exc()}"
                QMessageBox.warning(self, "发送失败", error_msg)
                return

        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建标题
        title_label = create_title_label("消息发送管理")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建消息内容区域
        message_group = create_group_box("消息内容")
        message_layout = QHBoxLayout()
        
        # 左侧消息列表和控制区域
        list_layout = QVBoxLayout()
        
        # 提示信息
        info_label = QLabel("添加要发送的内容（程序将按顺序发送）")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        list_layout.addWidget(info_label)
        
        # 消息列表
        self.msg = MyListWidget()
        self.clock.send_func = send_msg
        self.clock.prevent_func = self.wechat.prevent_offline
        list_layout.addWidget(self.msg)
        
        # 发送控制区域
        control_layout = QHBoxLayout()
        
        # 发送间隔设置
        send_interval = MySpinBox("发送间隔（秒）")
        send_interval.spin_box.setValue(1)  # 默认值设为1秒
        control_layout.addWidget(send_interval, 2)
        
        # 发送按钮
        send_btn = create_primary_button("发送消息")
        send_btn.clicked.connect(send_msg)
        control_layout.addWidget(send_btn, 1)
        
        list_layout.addLayout(control_layout)
        message_layout.addLayout(list_layout, 7)
        
        # 右侧按钮区域
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 内容操作区
        content_actions_group = create_group_box("内容操作")
        content_actions_layout = QVBoxLayout()
        
        load_btn = create_secondary_button("加载内容文件")
        load_btn.clicked.connect(load_text)
        
        text_btn = create_secondary_button("添加文本内容")
        text_btn.clicked.connect(add_text)
        
        file_btn = create_secondary_button("添加文件")
        file_btn.clicked.connect(add_file)
        
        del_btn = create_danger_button("删除选中内容")
        del_btn.clicked.connect(del_content)
        
        content_actions_layout.addWidget(load_btn)
        content_actions_layout.addWidget(text_btn)
        content_actions_layout.addWidget(file_btn)
        content_actions_layout.addWidget(del_btn)
        content_actions_group.setLayout(content_actions_layout)
        
        # 添加到按钮布局
        buttons_layout.addWidget(content_actions_group)
        buttons_layout.addStretch()
        
        message_layout.addLayout(buttons_layout, 3)
        message_group.setLayout(message_layout)
        
        main_layout.addWidget(message_group)
        
        # 添加热键提示
        hotkey_info = QLabel("提示: 按下 Ctrl+Alt 可以紧急停止发送")
        hotkey_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotkey_info.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-style: italic;")
        main_layout.addWidget(hotkey_info)
        
        return main_layout

    # 提供选择微信语言版本的按钮
    def init_language_choose(self):
        def switch_language():
            if lang_zh_CN_btn.isChecked():
                self.wechat.lc = WeChatLocale("zh-CN")
            elif lang_zh_TW_btn.isChecked():
                self.wechat.lc = WeChatLocale("zh-TW")
            elif lang_en_btn.isChecked():
                self.wechat.lc = WeChatLocale("en-US")

        # 创建布局
        layout = QVBoxLayout()
        
        # 提示信息
        info = QLabel("请确保选择的语言与您的微信客户端语言一致")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"font-weight: bold; color: {AppTheme.TEXT_PRIMARY};")
        layout.addWidget(info)

        # 语言选择按钮组
        lang_group = QButtonGroup(self)
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(20)
        radio_layout.setContentsMargins(10, 10, 10, 10)
        
        # 简体中文选项
        lang_zh_CN_btn = QRadioButton("简体中文 ✔")
        lang_group.addButton(lang_zh_CN_btn)
        radio_layout.addWidget(lang_zh_CN_btn)
        
        # 繁体中文选项
        lang_zh_TW_btn = QRadioButton("繁体中文")
        lang_group.addButton(lang_zh_TW_btn)
        radio_layout.addWidget(lang_zh_TW_btn)
        
        # 英文选项
        lang_en_btn = QRadioButton("English")
        lang_group.addButton(lang_en_btn)
        radio_layout.addWidget(lang_en_btn)

        # 默认选择简体中文
        lang_zh_CN_btn.setChecked(True)

        # 选择按钮的响应事件
        lang_zh_CN_btn.clicked.connect(lambda: self.update_radio_labels(lang_zh_CN_btn, lang_zh_TW_btn, lang_en_btn))
        lang_zh_TW_btn.clicked.connect(lambda: self.update_radio_labels(lang_zh_TW_btn, lang_zh_CN_btn, lang_en_btn))
        lang_en_btn.clicked.connect(lambda: self.update_radio_labels(lang_en_btn, lang_zh_CN_btn, lang_zh_TW_btn))
        
        # 连接语言切换函数
        lang_zh_CN_btn.clicked.connect(switch_language)
        lang_zh_TW_btn.clicked.connect(switch_language)
        lang_en_btn.clicked.connect(switch_language)

        layout.addLayout(radio_layout)
        
        # # 添加提示信息
        # tip_label = QLabel("* 请确保选择的语言与您的微信客户端语言一致")
        # tip_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-style: italic; font-size: 10px;")
        # tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(tip_label)

        return layout
    
    # 更新单选按钮标签，为选中的添加✔标记
    def update_radio_labels(self, selected, *others):
        # 为选中的按钮添加✔标记
        text = selected.text()
        if not text.endswith(" ✔"):
            selected.setText(f"{text} ✔")
        
        # 移除其他按钮的✔标记
        for btn in others:
            text = btn.text()
            if text.endswith(" ✔"):
                btn.setText(text[:-2])

    # 初始化微信设置界面
    def init_wechat_settings(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建标题
        title_label = create_title_label("微信设置")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 微信路径设置区域
        path_group = create_group_box("微信路径设置")
        path_layout = QVBoxLayout()
        
        # 显示微信exe路径
        path_info_layout = QHBoxLayout()
        path_info_layout.setSpacing(0)  # 设置组件之间的间距为0
        path_label = QLabel("当前路径:")
        path_info_layout.addWidget(path_label)
        self.path_label = QLabel("", self)
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet(f"background-color: white; padding: 8px; border-radius: 4px; border: 1px solid {AppTheme.BORDER};")
        path_info_layout.addWidget(self.path_label, 1)  # 设置路径标签占用剩余空间
        
        # 选择微信exe路径的按钮
        path_btn_layout = QHBoxLayout()
        self.path_btn = create_primary_button("选择微信打开路径")
        self.path_btn.clicked.connect(self.choose_path)
        path_btn_layout.addWidget(self.path_btn)
        path_btn_layout.addStretch()
        
        path_layout.addLayout(path_info_layout)
        path_layout.addLayout(path_btn_layout)
        path_group.setLayout(path_layout)
        main_layout.addWidget(path_group)
        
        # 语言设置区域
        lang_group = create_group_box("系统语言设置")
        lang_group.setLayout(self.init_language_choose())
        main_layout.addWidget(lang_group)
        
        # 添加一些额外的设置选项（可以根据需要扩展）
        extra_settings_group = create_group_box("其他设置")
        extra_settings_layout = QVBoxLayout()
        
        # 添加一个防止自动下线的toggle按钮
        prevent_offline_btn = QPushButton("防止自动下线")
        prevent_offline_btn.setCheckable(True)
        prevent_offline_btn.setChecked(False)
        prevent_offline_btn.clicked.connect(self.toggle_prevent_offline)
        prevent_offline_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                background-color: #e0e0e0;
                color: #212121;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:checked {
                background-color: #2979ff;
                color: white;
                font-weight: bold;
            }
        """)
        extra_settings_layout.addWidget(prevent_offline_btn)
        self.prevent_offline_btn = prevent_offline_btn
        
        extra_settings_group.setLayout(extra_settings_layout)
        main_layout.addWidget(extra_settings_group)
        
        # 添加一些空白区域
        main_layout.addStretch()
        
        return main_layout
    
    # 切换防止自动下线状态
    def toggle_prevent_offline(self):
        if self.clock.prevent_offline is True:
            self.clock.prevent_offline = False
            self.prevent_offline_btn.setChecked(False)
        else:
            # 弹出提示框
            QMessageBox.information(self, "防止自动下线", "防止自动下线已开启！每隔一小时自动点击微信窗口，防"
                                                      "止自动下线。请不要在正常使用电脑时使用该策略。")
            
            self.clock.prevent_offline = True
            self.prevent_offline_btn.setChecked(True)

    def initUI(self):
        # 应用Material Design样式表
        apply_material_stylesheet(QApplication.instance(), theme='light_blue.xml')
        
        # 主布局 - 使用选项卡布局
        main_layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        # 创建标题和版本信息
        # header_layout = QHBoxLayout()
        # title_label = create_title_label("EasyChat 微信助手")
        # title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # header_layout.addWidget(title_label)
        
        # 创建各个选项卡
        settings_tab = QWidget()
        settings_tab.setLayout(self.init_wechat_settings())

        contacts_tab = QWidget()
        contacts_tab.setLayout(self.init_choose_contacts())
        
        message_tab = QWidget()
        message_tab.setLayout(self.init_send_msg())
        
        schedule_tab = QWidget()
        schedule_tab.setLayout(self.init_clock())
        
        # 添加选项卡
        tab_widget.addTab(settings_tab, "微信设置")
        tab_widget.addTab(contacts_tab, "联系人管理")
        tab_widget.addTab(message_tab, "消息发送")
        tab_widget.addTab(schedule_tab, "定时任务")
        
        # 添加所有组件到主布局
        # main_layout.addLayout(header_layout)
        main_layout.addWidget(tab_widget)
        
        # 获取显示器分辨率并设置窗口大小
        screen = QApplication.instance().primaryScreen()
        screenRect = screen.geometry()
        height = screenRect.height()
        width = screenRect.width()
        
        # 设置窗口属性
        self.setLayout(main_layout)
        # self.setMinimumSize(int(width*0.25), int(height*0.7))
        self.setWindowTitle('EasyChat微信助手 v2.0')
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
    sys.exit(app.exec())