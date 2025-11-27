import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uiautomation as auto
from ui_auto_wechat import WeChat


def print_control_tree(control, depth=0, output_file=None, max_depth=20):
    """
    递归打印控件树
    Args:
        control: UI控件
        depth: 当前深度
        output_file: 输出文件句柄
        max_depth: 最大递归深度
    """
    if depth > max_depth:
        return

    indent = "  " * depth

    try:
        # 获取控件信息
        name = control.Name if hasattr(control, 'Name') else ''
        control_type = control.ControlTypeName if hasattr(control, 'ControlTypeName') else 'Unknown'
        automation_id = control.AutomationId if hasattr(control, 'AutomationId') else ''
        class_name = control.ClassName if hasattr(control, 'ClassName') else ''

        # 获取位置信息
        try:
            rect = control.BoundingRectangle
            position = f"({rect.left}, {rect.top}, {rect.width()}, {rect.height()})"
        except:
            position = "(?, ?, ?, ?)"

        # 构建输出行
        info_parts = [f"Depth={depth}"]
        if name:
            info_parts.append(f"Name='{name}'")
        info_parts.append(f"Type={control_type}")
        if automation_id:
            info_parts.append(f"AutomationId='{automation_id}'")
        if class_name:
            info_parts.append(f"Class='{class_name}'")
        info_parts.append(f"Rect={position}")

        line = f"{indent}[{', '.join(info_parts)}]\n"

        # 输出到文件和控制台
        output_file.write(line)
        print(line.rstrip())

        # 递归处理子控件
        try:
            children = control.GetChildren()
            for child in children:
                print_control_tree(child, depth + 1, output_file, max_depth)
        except:
            pass

    except Exception as e:
        error_line = f"{indent}[ERROR: {str(e)}]\n"
        output_file.write(error_line)
        print(error_line.rstrip())


def export_wechat_ui_tree():
    """导出微信UI树"""

    # 初始化微信客户端
    path = r"D:\Program Files (x86)\Weixin\Weixin.exe"
    wechat = WeChat(path, locale="zh-CN")

    print("\n[1] 打开微信...")
    wechat.open_wechat()
    time.sleep(2)

    print("\n[2] 获取微信窗口...")
    try:
        wechat_window = wechat.get_wechat()
        print(f"    [OK] 找到微信窗口: {wechat_window.Name}")
    except Exception as e:
        print(f"    [ERROR] 无法找到微信窗口: {e}")
        return

    print("\n[3] 导出UI树到 wechat_ui_tree.txt ...")
    output_path = "wechat_ui_tree.txt"

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            print_control_tree(wechat_window, 0, f, max_depth=50)

        print(f"\n文件保存在: {os.path.abspath(output_path)}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")

    except Exception as e:
        print(f"\n[ERROR] 导出失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        export_wechat_ui_tree()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()