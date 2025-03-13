from PyQt6.QtGui import QColor, QFont, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QLabel, QPushButton, QGroupBox, QButtonGroup, QApplication
from qt_material import apply_stylesheet

# 自定义样式覆盖
class StyleManager:
    @staticmethod
    def get_global_styles():
        """返回全局样式字符串"""
        return f"""
            QGroupBox#tab-group-box {{
                border: none;
                font-size: 14pt;
                font-weight: bold;
            }}

            QGroupBox#tab-group-box::title {{
                color: {AppTheme.TEXT_PRIMARY};
            }}

            QLabel.path-label {{
                background-color: white;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid {AppTheme.BORDER};
            }}
        """

def apply_material_stylesheet(app):
    """
    应用Material Design样式到应用程序
    
    参数:
        app: QApplication实例
        theme: 主题名称，默认为light_blue.xml
    """
    # 应用qt-material样式
    apply_stylesheet(app, theme='light_blue.xml')
    
    # 然后应用我们自己的全局样式覆盖
    app.setStyleSheet(app.styleSheet() + StyleManager.get_global_styles())
    
    return app

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
    TEXT_PRIMARY = "var(--primary)"  # 深灰色
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

# 创建选项卡分组框
def create_tab_group_box(title, layout=None):
    group_box = QGroupBox(title)
    group_box.setObjectName("tab-group-box")
    # group_box.setStyleSheet(f"QGroupBox#tab-group-box {{ border: none; font-size: 14pt; font-weight: bold; color: {AppTheme.TEXT_PRIMARY} !important; }}")
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