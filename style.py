from PyQt6.QtGui import QColor, QFont, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QLabel, QPushButton, QGroupBox, QButtonGroup

# 定义应用的主题颜色 - 这些颜色仅作为备用，主要样式由material_style提供
class AppTheme:
    # 主色调
    PRIMARY = "#2979ff"  # 蓝色 - 与material light_blue主题匹配
    PRIMARY_LIGHT = "#75a7ff"
    PRIMARY_DARK = "#004ecb"
    
    # 辅助色
    SECONDARY = "#00b0ff"  # 绿色
    SECONDARY_LIGHT = "#69e2ff"
    SECONDARY_DARK = "#0081cb"
    
    # 警告色
    WARNING = "#ffc107"  # 黄色
    DANGER = "#f44336"   # 红色
    
    # 背景色
    BACKGROUND = "#f5f5f5"  # 浅灰色
    CARD_BACKGROUND = "#ffffff"  # 白色
    
    # 文本颜色
    TEXT_PRIMARY = "#212121"  # 深灰色
    TEXT_SECONDARY = "#757575"  # 中灰色
    TEXT_HINT = "#9e9e9e"  # 浅灰色
    TEXT_DISABLED = "#bdbdbd"  # 更浅的灰色
    
    # 边框颜色
    BORDER = "#e0e0e0"

# 创建标题标签
def create_title_label(text):
    label = QLabel(text)
    label.setProperty("title", "true")
    return label

# 创建分组框
def create_group_box(title, layout=None):
    group_box = QGroupBox(title)
    if layout:
        group_box.setLayout(layout)
    return group_box

# 创建主要按钮
def create_primary_button(text, on_click=None):
    button = QPushButton(text)
    if on_click:
        button.clicked.connect(on_click)
    return button

# 创建次要按钮
def create_secondary_button(text, on_click=None):
    button = QPushButton(text)
    button.setProperty("secondary", "true")
    if on_click:
        button.clicked.connect(on_click)
    return button

# 创建警告按钮
def create_warning_button(text, on_click=None):
    button = QPushButton(text)
    button.setProperty("warning", "true")
    if on_click:
        button.clicked.connect(on_click)
    return button

# 创建危险按钮
def create_danger_button(text, on_click=None):
    button = QPushButton(text)
    button.setProperty("danger", "true")
    if on_click:
        button.clicked.connect(on_click)
    return button