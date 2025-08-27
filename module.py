import sys
import time
import datetime
import threading
import keyboard

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
        # 是否防止自动下线
        self.prevent_offline = False
        self.prevent_func = None
        # 每隔多少分钟进行一次防止自动下线操作
        self.prevent_count = 60

        # 新增：用于存储已执行过的任务标识，防止重复执行
        self.executed_tasks = set()

        # 用于防止掉线的内部计时器
        self._prevent_timer = 0

    def __del__(self):
        self.wait()

    def run(self):
        import uiautomation as auto
        with auto.UIAutomationInitializerInThread():
            # 初始化防止掉线的计时器，设置为 prevent_count 分钟对应的秒数
            self._prevent_timer = self.prevent_count * 60

            while self.time_counting:
                now = datetime.datetime.now()
                next_event_time = None

                # --- 1. 遍历列表，查找最近的下一个闹钟时间 ---
                try:
                    for i in range(self.clocks.count()):
                        task_id = self.clocks.item(i).text()
                        # 如果任务已经执行过，则跳过
                        if task_id in self.executed_tasks:
                            continue

                        parts = task_id.split(" ")
                        clock_str = " ".join(parts[:5])
                        dt_obj = datetime.datetime.strptime(clock_str, "%Y %m %d %H %M")

                        # 只关心未来的任务
                        if dt_obj > now:
                            # 如果是第一个找到的未来任务，或者比已知的下一个任务更早
                            if next_event_time is None or dt_obj < next_event_time:
                                next_event_time = dt_obj
                except Exception as e:
                    # 在UI更新列表时，直接读取可能会有瞬时错误，做个保护
                    print(f"读取闹钟列表时出错: {e}")
                    time.sleep(1)  # 出错时短暂休眠后重试
                    continue

                # --- 2. 计算休眠时间 ---
                sleep_seconds = 60  # 默认休眠60秒，如果没有找到任何未来任务

                if next_event_time:
                    delta = (next_event_time - now).total_seconds()
                    # 确保休眠时间不为负
                    sleep_seconds = max(0, delta)

                # --- 3. 整合“防止掉线”的逻辑 ---
                if self.prevent_offline:
                    # 取“下一个闹钟”和“下一次防掉线”中更早发生的一个
                    sleep_seconds = min(sleep_seconds, self._prevent_timer)

                # --- 4. 执行休眠 ---
                # sleep_seconds 可能是小数，time.sleep支持
                time.sleep(sleep_seconds)

                # 更新防止掉线的内部计时器
                self._prevent_timer -= sleep_seconds
                if self._prevent_timer <= 0:
                    self._prevent_timer = 0  # 避免变为很大的负数

                # --- 5. 休眠结束，检查并执行到期的任务 ---
                now = datetime.datetime.now()  # 获取唤醒后的精确时间

                # 检查并执行到期的闹钟
                try:
                    for i in range(self.clocks.count()):
                        task_id = self.clocks.item(i).text()
                        if task_id in self.executed_tasks:
                            continue

                        parts = task_id.split(" ")
                        st_ed = parts[5]
                        st, ed = st_ed.split('-')
                        clock_str = " ".join(parts[:5])
                        dt_obj = datetime.datetime.strptime(clock_str, "%Y %m %d %H %M")

                        # 如果任务时间已到或已错过
                        if dt_obj <= now:
                            if self.send_func:
                                self.send_func(st=int(st), ed=int(ed))
                            # 记录为已执行
                            self.executed_tasks.add(task_id)
                except Exception as e:
                    print(f"执行任务时读取闹钟列表出错: {e}")

                # 检查并执行防止掉线
                if self.prevent_offline and self._prevent_timer <= 0:
                    if self.prevent_func:
                        self.prevent_func()
                    # 重置计时器
                    self._prevent_timer = self.prevent_count * 60


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
        # self.label.setAlignment(Qt.AlignCenter)

        # 初始化计数器
        self.spin_box = QSpinBox()
        # self.spin_box.valueChanged.connect(self.valuechange)

        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)
        self.setLayout(layout)

    # def valuechange(self):
    #     self.label.setText(f"{self.desc}: {self.spin_box.value()}")