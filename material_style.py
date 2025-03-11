from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

# 自定义样式覆盖
EXTRA_STYLES = {
    'QListWidget::item:selected': '''
        background-color: #2979ff;
        color: #ffffff;
        font-weight: bold;
    ''',
    'QLineEdit': '''
        border: 1px solid #bdbdbd;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        selection-background-color: #2979ff;
    ''',
    'QLineEdit:focus': '''
        border: 2px solid #2979ff;
    ''',
    'MyListWidget QLineEdit': '''
        border: 2px solid #2979ff;
        border-radius: 4px;
        padding: 6px;
        background-color: #f5f5f5;
        selection-background-color: #2979ff;
        color: #212121;
        font-weight: normal;
    ''',
    'QListWidget::item:hover': '''
        background-color: #e3f2fd;
        color: #212121;
    '''
}

# 可用的主题:
# 'dark_amber.xml',
# 'dark_blue.xml',
# 'dark_cyan.xml',
# 'dark_lightgreen.xml',
# 'dark_pink.xml',
# 'dark_purple.xml',
# 'dark_red.xml',
# 'dark_teal.xml',
# 'dark_yellow.xml',
# 'light_amber.xml',
# 'light_blue.xml',
# 'light_cyan.xml',
# 'light_cyan_500.xml',
# 'light_lightgreen.xml',
# 'light_pink.xml',
# 'light_purple.xml',
# 'light_red.xml',
# 'light_teal.xml',
# 'light_yellow.xml'

def apply_material_stylesheet(app, theme='light_blue.xml'):
    """
    应用Material Design样式到应用程序
    
    参数:
        app: QApplication实例
        theme: 主题名称，默认为light_blue.xml
    """
    # 应用qt-material样式
    apply_stylesheet(app, theme=theme, extra=EXTRA_STYLES)
    
    return app