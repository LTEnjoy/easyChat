#Now the LLMs can be used to support the auto reply feature
#调用qianfan接口
import time
import time
import os
from ui_auto_wechat import WeChat
os.environ["QIANFAN_ACCESS_KEY"] = "your access key"
os.environ["QIANFAN_SECRET_KEY"] = "your secret key"


if __name__ == "__main__":
    #Set the wechat path
    wechat_path = "C:\Program Files\Tencent\WeChat\WeChat.exe"

    wechat = WeChat(wechat_path)
    #Set the auto reply names and a retard list used for quick replying BS meaningless words. 
    auto_reply_names = ["group1", "contact1"]
    wechat.set_auto_reply(auto_reply_names)
    wechat.set_retard_list(["retard1"])
    '''
        Current check_new_msg function has a full pipeline of checking new msg -> auto reply meg -> loop the steps above.
        So one function is enough for doing the jobs.
    '''
    wechat.check_new_msg()
