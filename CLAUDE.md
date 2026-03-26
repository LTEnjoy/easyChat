# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasyChat is a PC WeChat automation assistant that uses UI automation to control the WeChat desktop client. It provides scheduled messaging, bulk messaging, and auto-reply functionality through a PyQt5 GUI. The project uses `uiautomation` to interact with WeChat's UI controls since web WeChat is no longer available.

**Important**: This project currently supports WeChat version 4.1.8+. Some features (like `check_new_msg`, `get_dialogs`, `save_dialog_pictures`) are marked as `NotImplementedError` and have not been adapted to the new WeChat version.

## Prerequisites

**CRITICAL**: Windows Narrator mode (讲述人) must be enabled for `uiautomation` to work properly. Without it, the application cannot detect WeChat UI controls. This is the #1 cause of runtime failures.

## Key Dependencies

Core dependencies (from requirements.txt, which has UTF-16 encoding):
- **PyQt5 5.15.7** - GUI framework
- **uiautomation 2.0.17** - Windows UI automation library
- **pyperclip 1.8.2** - Clipboard operations for text
- **keyboard 0.13.5** - Global hotkey handling (Ctrl+Alt+Q to interrupt)
- **pyautogui 0.9.54** - Additional automation utilities
- **pandas 2.0.3** - Data handling for contact lists
- **pyinstaller 5.12.0** - Executable packaging
- **pywin32 304** - Windows API access

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
This uses PyInstaller to create a standalone `.exe` file. The actual command is:
```bash
pyinstaller.exe -Fw --noupx wechat_gui.py
```
Output: `dist/wechat_gui.exe`

### Testing Core Functions
Run the `__main__` section in `ui_auto_wechat.py` with your WeChat path:
```python
path = "D:\Program Files (x86)\Weixin\Weixin.exe"
wechat = WeChat(path, locale="zh-CN")
# Uncomment specific test functions
```

## Key Technical Details

### User Interaction Features
- **Interrupt Hotkey**: Users can press `Ctrl+Alt+Q` to terminate sending operations mid-process (handled by `keyboard` library global hook in `wechat_gui.py`)
- **Anti-Auto-Logout**: Optional feature to prevent WeChat from automatically logging out during long idle periods (triggers every hour)
- **Multi-File Selection**: File upload dialogs support selecting multiple files simultaneously

### UI Automation Strategy
- Uses `uiautomation` library to locate WeChat controls by `Depth`, `Name`, `ClassName`, and `foundIndex`
- Control depths are hardcoded (e.g., `Depth=13` for search box) and may break with WeChat UI updates
- Search strategy: Types contact name in search box, waits 0.3s, then clicks first non-"XTableCell" result
- Message sending: Uses clipboard paste (`Ctrl+V`) instead of direct text input for reliability

### Configuration Management
- **Auto-Save**: All user settings stored in `wechat_config.json` with automatic persistence after EVERY user action (add/delete contacts, messages, schedules). No manual save required.
- Configuration structure:
  ```json
  {
    "settings": {"wechat_path": "", "send_interval": 0, "system_version": "new", "language": "zh-CN"},
    "contacts": [],
    "messages": [],
    "schedules": []
  }
  ```
- Config is loaded automatically on startup and saved after each modification in GUI

### Message Format in GUI
Messages are stored as colon-separated strings:
- Text: `{rank}:text:{to}:{at_names}:{content}`
- File: `{rank}:file:{to}:{path}`
- `to` can be "all" or comma-separated user indices like "1,2,3"
- Content supports `\n` for newlines (e.g., "Hello\nWorld" sends as two lines)

### Bulk Loading from TXT Files
- **Users TXT**: One contact name per line, loaded via "加载用户txt文件" button
- **Content TXT**: Format `all:content` or `1,2,3:content` per line (colon-separated: recipient list, then message)
- TXT loading only supports text messages, not file attachments

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

1. **WeChat Version Compatibility**: Hardcoded control depths break when WeChat updates its UI. Use `automation.py` to inspect the new control tree. Latest supported version: 4.1.8+ (as of 2026/03/26).

2. **WeChat Launch Method**: Recent versions (2026/03/09 fix) use a new launch method to avoid triggering new login popup. Don't modify WeChat startup logic without understanding the workaround.

3. **Search Box Behavior**: Groups no longer appear as first search result. Code now skips "XTableCell" items to find actual contacts (line 116 in ui_auto_wechat.py).

4. **Clipboard Race Conditions**: 0.3s delays after clipboard operations are critical. Removing them causes paste failures.

5. **NotImplementedError Methods**: `check_new_msg()`, `get_dialogs()`, `save_dialog_pictures()`, and `get_dialogs_by_time_blocks()` are not adapted to WeChat 4.1 and will raise exceptions.

## File Encoding Note

`requirements.txt` is UTF-16 encoded (appears as spaced characters when read as UTF-8). Key dependencies are listed in the "Key Dependencies" section above. Install with:
```bash
pip install -r requirements.txt
```

## Code Style Observations

- Chinese comments and variable names mixed with English
- Minimal error handling (relies on try-except at high level)
- GUI uses nested layouts (QVBoxLayout, QHBoxLayout) without Qt Designer
- No unit tests present
- Code is actively maintained (latest update: 2026/03/26)
