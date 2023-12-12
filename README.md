# BS words auto replying bot
## Introduction
Based on https://github.com/LTEnjoy/easyChat <br>
You can use this bot to annoy your friends by automatically replying constant nonsense generated words. <br>
And qianfan api is used for LLMs part. <br>

## Disadvantage
**Windows Only** and during program's running you can't operate your PC. Which means it is **fully occupied** when running.

## Quick Start
Set your access key and secret key and `wechat.exe` path in `main.py`. <br>
And you can also adjust your prompt and model in `ui_auto_wechat.py`, `get_result()` function.

```
Set-Location easyChat
pip install -r requirements.txt
python main.py
```