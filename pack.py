import os


# 用来自动打包成exe程序
def main():
    cmd = f"pyinstaller.exe -Fw --noupx --collect-submodules versions D:\PycharmProjects\easyChat\wechat_gui.py --distpath D:\PycharmProjects\easyChat\dist"

    # 执行命令并打印输出
    result = os.system(cmd)


if __name__ == '__main__':
    main()
