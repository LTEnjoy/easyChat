import sys
import time
import threading
import keyboard

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
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
        # 是否防止自动下线
        self.prevent_offline = False
        self.prevent_func = None
        # 每隔多少分钟进行一次防止自动下线操作
        self.prevent_count = 60

    def __del__(self):
        self.wait()

    def run(self):
        cnt = 60
        while self.time_counting:
            localtime = time.localtime(time.time())
            year = localtime.tm_year
            month = localtime.tm_mon
            day = localtime.tm_mday
            hour = localtime.tm_hour % 24
            min = localtime.tm_min % 60

            for i in range(self.clocks.count()):
                clock_year, clock_month, clock_day, clock_hour, clock_min, st_ed = self.clocks.item(i).text().split(" ")
                st, ed = st_ed.split('-')
                if (int(clock_hour) == hour and int(clock_min) == min and int(clock_year) == year and
                        int(clock_month) == month and int(clock_day) == day):
                    self.send_func(st=int(st), ed=int(ed))
                    # self.send_func()
                    
            if self.prevent_offline and cnt % self.prevent_count == 0:
                self.prevent_func()

            time.sleep(60)
            cnt += 1


class MyListWidget(QListWidget):
    """支持双击可编辑的QListWidget"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # 设置选择多个

        # 双击可编辑
        self.edited_item = self.currentItem()
        self.close_flag = True
        self.doubleClicked.connect(self.item_double_clicked)
        self.currentItemChanged.connect(self.close_edit)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        """回车事件，关闭edit"""
        super().keyPressEvent(e)
        if e.key() == Qt.Key.Key_Return:
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


class MultiInputDialog(QDialog):
    """
    用于用户输入的输入框，可以根据传入的参数自动创建输入框
    """
    def __init__(self, inputs: list, default_values: list = None, parent=None) -> None:
        """
        inputs: list, 代表需要input的标签，如['姓名', '年龄']
        default_values: list, 代表默认值，如['张三', '18']
        """
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        self.inputs = []
        for n, i in enumerate(inputs):
            layout.addWidget(QLabel(i))
            input = QLineEdit(self)

            # 设置默认值
            if default_values is not None:
                input.setText(default_values[n])

            layout.addWidget(input)
            self.inputs.append(input)
            
        ok_button = QPushButton("确认")
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_input(self):
        """获取用户输入"""
        return [i.text() for i in self.inputs]


class FileDialog(QDialog):
    """
    文件选择框
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.inputs = []
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("请指定发送给哪些用户(1,2,3代表发送给前三位用户)，如需全部发送请忽略此项"))
        input = QLineEdit(self)
        layout.addWidget(input)
        self.inputs.append(input)
        
        # 选择文件
        choose_layout = QHBoxLayout()

        path = QLineEdit(self)
        choose_layout.addWidget(path)
        self.inputs.append(path)

        file_button = QPushButton("选择文件")
        file_button.clicked.connect(self.select)
        choose_layout.addWidget(file_button)

        layout.addLayout(choose_layout)
        
        # 确认按钮
        ok_button = QPushButton("确认")
        ok_button.clicked.connect(self.accept)

        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def select(self):
        path_input = self.inputs[1]
        path = QFileDialog.getOpenFileName(self, '打开文件', '/home')[0]
        if path != "":
            path_input.setText(path)
    
    def get_input(self):
        """获取用户输入"""
        return [i.text() for i in self.inputs]


class MySpinBox(QWidget):
    def __init__(self, desc: str, **kwargs):
        """
        附带标签的SpinBox
        Args:
            desc: 默认的标签
        """
        super().__init__(**kwargs)

        layout = QHBoxLayout()

        # 初始化标签
        self.desc = desc
        self.label = QLabel(desc)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 初始化计数器
        self.spin_box = QSpinBox()
        # self.spin_box.valueChanged.connect(self.valuechange)

        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)
        self.setLayout(layout)

    # def valuechange(self):
    #     self.label.setText(f"{self.desc}: {self.spin_box.value()}")