import os


# 用来自动打包成exe程序
def main():
    # cmd = f"pyinstaller.exe -Fw wechat_gui.py"
    cmd = f"pyinstaller.exe -Fw wechat_gui_auto_replay.py"

    # 执行命令并打印输出
    result = os.system(cmd)


if __name__ == '__main__':
    main()
