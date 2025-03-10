import os
import sys
import subprocess


# 用来自动打包成exe程序
def main():
    # 检测是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("警告：当前不在虚拟环境中运行。建议在虚拟环境中执行打包操作。")
        response = input("是否继续打包？(y/n): ")
        if response.lower() != 'y':
            print("打包已取消")
            return
    
    cmd = f"pyinstaller.exe -Fw wechat_gui.py"

    result = subprocess.call(cmd, shell=True)
    
    if result == 0:
        print("打包成功！可执行文件位于 dist 目录中")
    else:
        print(f"打包失败，错误代码: {result}")


if __name__ == '__main__':
    main()