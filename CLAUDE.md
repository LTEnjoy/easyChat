# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasyChat is a PC WeChat automation assistant that uses UI automation to control the WeChat desktop client. It provides scheduled messaging, bulk messaging, and auto-reply functionality through a PyQt5 GUI. The project uses `uiautomation` to interact with WeChat's UI controls since web WeChat is no longer available.

**Important**: This project currently supports WeChat version 4.1. Some features (like `check_new_msg`, `get_dialogs`, `save_dialog_pictures`) are marked as `NotImplementedError` and have not been adapted to the new WeChat version.

## Architecture

### Core Components

1. **ui_auto_wechat.py** - Core WeChat automation logic
   - `WeChat` class: Main automation controller that uses `uiautomation` to find and interact with WeChat UI controls
   - Handles contact search, message sending, file sending, contact extraction, and group extraction
   - Uses clipboard operations (`pyperclip`, `setClipboardFiles`) for text and file transfers
   - Supports multi-language WeChat clients (zh-CN, zh-TW, en-US) via `WeChatLocale`

2. **wechat_gui.py** - PyQt5 GUI application
   - `WechatGUI` class: Main window that orchestrates all UI components
   - Manages configuration persistence via `wechat_config.json` (auto-saves user actions)
   - Integrates with `ClockThread` for scheduled messaging
   - Uses global hotkey (Ctrl+Alt) to interrupt sending operations

3. **wechat_locale.py** - Internationalization support
   - `WeChatLocale` class: Provides localized UI element names for different WeChat language versions
   - Critical for finding UI controls in different language environments

4. **module.py** - Custom PyQt5 widgets
   - Reusable UI components like `MyListWidget`, `MySpinBox`, `ClockThread`, etc.

5. **clipboard.py** - File clipboard operations
   - `setClipboardFiles()`: Copies files to clipboard for sending via Ctrl+V

6. **automation.py** - UI control tree visualization tool
   - Helper for developers to inspect WeChat's UI control hierarchy

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python wechat_gui.py
```

### Building Executable
```bash
python pack.py
```
This uses PyInstaller to create a standalone `.exe` file.

### Testing Core Functions
Run the `__main__` section in `ui_auto_wechat.py` with your WeChat path:
```python
path = "D:\Program Files (x86)\Weixin\Weixin.exe"
wechat = WeChat(path, locale="zh-CN")
# Uncomment specific test functions
```

## Key Technical Details

### UI Automation Strategy
- Uses `uiautomation` library to locate WeChat controls by `Depth`, `Name`, `ClassName`, and `foundIndex`
- Control depths are hardcoded (e.g., `Depth=13` for search box) and may break with WeChat UI updates
- Search strategy: Types contact name in search box, waits 0.3s, then clicks first non-"XTableCell" result
- Message sending: Uses clipboard paste (`Ctrl+V`) instead of direct text input for reliability

### Configuration Management
- All user settings stored in `wechat_config.json` with structure:
  ```json
  {
    "settings": {"wechat_path": "", "send_interval": 0, "system_version": "new", "language": "zh-CN"},
    "contacts": [],
    "messages": [],
    "schedules": []
  }
  ```
- Auto-saves after every user action (add/delete contacts, messages, schedules)

### Message Format in GUI
Messages are stored as colon-separated strings:
- Text: `{rank}:text:{to}:{at_names}:{content}`
- File: `{rank}:file:{to}:{path}`
- `to` can be "all" or comma-separated user indices like "1,2,3"

### Scheduled Messaging
- `ClockThread` in `module.py` checks time every second
- Schedule format: `{year} {month} {day} {hour} {min} {start}-{end}`
- `start-end` specifies which messages to send (by index)

### Contact Extraction Limitations
The `find_all_contacts()` method has known reliability issues:
- WeChat's UI organizes contact info ambiguously (nickname, note, label separated by spaces)
- Uses `rsplit(" ", maxsplit=2)` which fails if names/notes contain spaces
- Scrolls through contact list with retry logic (3 failed attempts before stopping)

## Common Pitfalls

1. **WeChat Version Compatibility**: Hardcoded control depths break when WeChat updates its UI. Use `automation.py` to inspect the new control tree.

2. **Search Box Behavior**: Groups no longer appear as first search result. Code now skips "XTableCell" items to find actual contacts (line 116 in ui_auto_wechat.py).

3. **Narrator Mode Required**: WeChat must have Windows Narrator mode enabled for `uiautomation` to work properly (mentioned in README).

4. **Clipboard Race Conditions**: 0.3s delays after clipboard operations are critical. Removing them causes paste failures.

5. **NotImplementedError Methods**: `check_new_msg()`, `get_dialogs()`, `save_dialog_pictures()`, and `get_dialogs_by_time_blocks()` are not adapted to WeChat 4.1 and will raise exceptions.

## File Encoding Note

`requirements.txt` appears to have encoding issues (shows as binary characters). Dependencies include:
- PyQt5, uiautomation, pyperclip, keyboard, pandas, pyautogui, pyinstaller

## Code Style Observations

- Chinese comments and variable names mixed with English
- Minimal error handling (relies on try-except at high level)
- GUI uses nested layouts (QVBoxLayout, QHBoxLayout) without Qt Designer
- No unit tests present
