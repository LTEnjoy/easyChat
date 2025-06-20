import sys
import time
import os
import itertools
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
                    "language": "zh-CN",
                },
                "contacts": [],
                "messages": [],
                "schedules": [],
            }
            self.save_config()

        self.wechat = WeChat(self.config["settings"]["wechat_path"])
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
    
    # 自动回复线程
    #自动回复设定界面
    def init_auto_reply(self):
        # 自动回复配置
        auto_reply_config = self.config.setdefault("auto_reply", {
            "enabled": False,
            "start_time": "09:00",
            "end_time": "18:00",
            "interval": 10,
            "message": "我现在有事不在，稍后回复。"
        })

        # 设置自动回复配置
        def set_auto_reply_config():
            try:
                # 获取输入的值
                start_time = start_time_edit.text()
                end_time = end_time_edit.text()
                interval = int(interval_edit.text())
                message = message_edit.toPlainText()
                
                # 验证时间格式
                if not (self.validate_time(start_time) and self.validate_time(end_time)):
                    QMessageBox.warning(self, "错误", "时间格式不正确，请使用HH:MM格式(英文输入下的冒号)")
                    return
                    
                # 更新配置
                auto_reply_config.update({
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval": interval,
                    "message": message
                })
                self.save_config()
                QMessageBox.information(self, "成功", "自动回复设置已保存")
            except ValueError:
                QMessageBox.warning(self, "错误", "请输入有效的数字作为间隔时间")

        # 开启/关闭自动回复
        def toggle_auto_reply():
            if auto_reply_config["enabled"]:
                auto_reply_config["enabled"] = False
                auto_reply_btn.setStyleSheet("color:black")
                auto_reply_btn.setText("开启自动回复")
                QMessageBox.information(self, "提示", "自动回复已关闭")
            else:
                # 验证设置
                if not auto_reply_config["message"]:
                    QMessageBox.warning(self, "错误", "请先设置自动回复内容")
                    return
                    
                auto_reply_config["enabled"] = True
                auto_reply_btn.setStyleSheet("color:red")
                auto_reply_btn.setText("关闭自动回复")
                
                # 启动自动回复循环
                start_auto_reply_loop()
                QMessageBox.information(self, "提示", "自动回复已开启")
            
            self.save_config()

        # 启动自动回复循环
        def start_auto_reply_loop():
            # 设置自动回复
            self.wechat.set_auto_reply([])
            self.wechat.auto_reply_msg = auto_reply_config["message"]
            
            # 创建定时器来定期检查消息
            self.auto_reply_timer = QTimer()
            self.auto_reply_timer.timeout.connect(check_and_reply)
            self.auto_reply_timer.start(auto_reply_config["interval"] * 1000)  # 转换为毫秒

        # 检查并回复消息
        def check_and_reply():
            if not auto_reply_config["enabled"]:
                self.auto_reply_timer.stop()
                return
                
            current_time = time.strftime("%H:%M")
            start_h, start_m = map(int, auto_reply_config["start_time"].split(':'))
            end_h, end_m = map(int, auto_reply_config["end_time"].split(':'))
            current_h, current_m = map(int, current_time.split(':'))
            
            # 检查当前时间是否在设定时间段内
            if ((current_h > start_h or (current_h == start_h and current_m >= start_m)) and
                (current_h < end_h or (current_h == end_h and current_m <= end_m))):
                self.wechat.check_new_msg()

        hbox = QHBoxLayout()

        # 左边的设置界面
        settings_vbox = QVBoxLayout()
        
        # 时间段设置
        time_hbox = QHBoxLayout()
        time_hbox.addWidget(QLabel("开始时间:"))
        start_time_edit = QLineEdit(auto_reply_config["start_time"])
        time_hbox.addWidget(start_time_edit)
        time_hbox.addWidget(QLabel("结束时间:"))
        end_time_edit = QLineEdit(auto_reply_config["end_time"])
        time_hbox.addWidget(end_time_edit)
        settings_vbox.addLayout(time_hbox)
        
        # 间隔时间设置
        interval_hbox = QHBoxLayout()
        interval_hbox.addWidget(QLabel("检查间隔(秒):"))
        interval_edit = QLineEdit(str(auto_reply_config["interval"]))
        interval_hbox.addWidget(interval_edit)
        settings_vbox.addLayout(interval_hbox)
        
        # 回复内容设置
        settings_vbox.addWidget(QLabel("回复内容:"))
        message_edit = QTextEdit()
        message_edit.setPlainText(auto_reply_config["message"])
        settings_vbox.addWidget(message_edit)
        
        hbox.addLayout(settings_vbox)

        # # 右边的按钮界面
        # vbox = QVBoxLayout()
        # vbox.stretch(1)


        # 保存设置按钮
        save_btn = QPushButton("保存自动回复设置")
        save_btn.clicked.connect(set_auto_reply_config)
        settings_vbox.addWidget(save_btn)

        # 自动回复开关按钮
        auto_reply_btn = QPushButton("开启自动回复" if not auto_reply_config["enabled"] else "关闭自动回复")
        auto_reply_btn.setStyleSheet("color:red" if auto_reply_config["enabled"] else "color:black")
        auto_reply_btn.clicked.connect(toggle_auto_reply)
        settings_vbox.addWidget(auto_reply_btn)

        # 防止自动下线按钮
        prevent_btn = QPushButton("防止自动下线：（目前关闭）")
        prevent_btn.clicked.connect(self.prevent_offline)
        settings_vbox.addWidget(prevent_btn)


        info = QLabel("使用说明：\n1、点击“选择微信打开路径”\n"
                      "2、选择你微信的位置(点选桌面微信图标即可)\n"
                      "3、设置自动回复的时间段和内容（检查间隔默认即可）\n"
                      "4、点击“保存自动回复设置”\n"
                      "5、启用自动回复时需要将“文件传输助手”置顶，并取消其他置顶，方可正常使用。（奇怪的bug）\n"
                      "6、点击“开启自动回复”按钮开始自动回复\n"
                      "(如果需要停止自动回复，请点击“关闭自动回复”按钮。)\n"
                      
                      "########注意########\n"
                      "因为是模拟的点击事件，如果在设定使用事件内操作电脑，记得先停止自动回复\n"
                      "########注意########\n"
                      "“防止自动下线”只有在出现微信出现自动下线时启用（一般用不上）\n"
                      )
        label_font = info.font()
        label_font.setPointSize(12)  # 设置字体大小
        label_font.setFamily("Microsoft YaHei")   # 设置字体
        info.setFont(label_font)
        info.setWordWrap(True)
        settings_vbox.addWidget(info)

        hbox.addLayout(settings_vbox)

        return hbox

    def validate_time(self, time_str):
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def prevent_offline(self):
        if self.clock.prevent_offline is True:
            self.clock.prevent_offline = False
            self.sender().setStyleSheet("color:black")
            self.sender().setText("防止自动下线：（目前关闭）")
        else:
            QMessageBox.information(self, "防止自动下线", "防止自动下线已开启！每隔一小时自动点击微信窗口，防止自动下线。请不要在正常使用电脑时使用该策略。")
            self.clock.prevent_offline = True
            self.sender().setStyleSheet("color:red")
            self.sender().setText("防止自动下线：（目前开启）")
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

        # 自动回复界面
        auto_reply = self.init_auto_reply()

        vbox.addWidget(self.path_label)
        vbox.addWidget(self.path_btn)
        vbox.addLayout(lang)
        vbox.addLayout(auto_reply)
 
        vbox.addStretch(5)

        # qle.textChanged[str].connect(self.onChanged)

        #获取显示器分辨率
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        height = screenRect.height()
        width = screenRect.width()

        self.setLayout(vbox)
        # self.setFixedSize(width*0.2, height*0.6)
        self.setWindowTitle('EasyChat微信助手·自动回复(原作者：LTEnjoy)')
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


