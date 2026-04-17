# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasyChat is a Windows-only PC WeChat automation assistant that uses UI automation to control the WeChat desktop client. It provides scheduled messaging, bulk messaging, and contact extraction through a PyQt5 GUI. The project uses `uiautomation` to interact with WeChat's UI controls since web WeChat is no longer available.

**Supported WeChat version**: 4.1.8+ (as of 2026/03/26). Earlier versions (3.9) are not supported.

**Unimplemented methods**: `check_new_msg()`, `get_dialogs()`, `save_dialog_pictures()`, and `get_dialogs_by_time_blocks()` raise `NotImplementedError` — they have not been adapted to WeChat 4.1.

## Prerequisites

**CRITICAL**: Windows Narrator (讲述人) must be enabled for `uiautomation` to detect WeChat UI controls. This is the #1 cause of runtime failures.

## Development Commands

```bash
# Setup
pip install -r requirements.txt   # requirements.txt is UTF-16 encoded; pip handles it fine

# Run GUI
python wechat_gui.py

# Build standalone .exe (output: dist/wechat_gui.exe)
python pack.py
# Equivalent to: pyinstaller.exe -Fw --noupx wechat_gui.py

# Inspect WeChat's live UI control tree (use when WeChat updates break automation)
python automation.py [-t delay] [-d depth] [-r root] [-c cursor]
# Output also written to @AutomationLog.txt
```

**Testing core automation**: Edit the `__main__` block in `ui_auto_wechat.py`, set your WeChat path, and uncomment specific test calls. No test framework is used.

## Architecture

The application layers are:

```
wechat_gui.py        ← PyQt5 UI, config persistence, hotkey handling
    │
    ├── module.py    ← ClockThread (scheduler), custom widgets
    │
    └── ui_auto_wechat.py  ← WeChat automation (the core engine)
            │
            ├── wechat_locale.py  ← Localized UI element names
            └── clipboard.py      ← File clipboard operations (win32)
```

### ui_auto_wechat.py — Core Automation Engine

The `WeChat` class wraps `uiautomation` to control WeChat's desktop UI. Key design decisions:

- **UI control depths are hardcoded** (e.g., `Depth=15` for search box). These break when WeChat updates its UI structure. Use `automation.py` to re-inspect the control tree after any WeChat update.
- **All text input uses clipboard paste** (`pyperclip` → Ctrl+V) instead of direct typing, for reliability. The 0.3s delays after clipboard operations are critical — removing them causes paste failures.
- **WeChat is opened via Ctrl+Alt+W** (not by launching the `.exe` directly). This avoids triggering the new login popup (2026/03/09 fix). Do not change the startup logic without understanding this workaround.
- **Contact search skips `XTableCell` items** to avoid selecting groups instead of contacts (2025/12/02 fix). `search_wait` (default 0.3s, configurable in settings) controls how long to wait for search results.
- `find_all_contacts()` returns a pandas DataFrame. It uses `rsplit(" ", maxsplit=2)` to parse contact info, which fails if names or notes contain spaces.

### wechat_gui.py — GUI & Orchestration

`WechatGUI(QWidget)` owns the main window. Every user action (add/delete contacts, messages, schedules) auto-saves to `wechat_config.json` immediately — there is no manual save.

Config structure:
```json
{
  "settings": {"wechat_path": "", "send_interval": 0, "search_wait": 0.3, "system_version": "new", "language": "zh-CN"},
  "contacts": ["1:name1", "2:name2"],
  "messages": ["1:text:all::content", "2:file:1,2::path"],
  "schedules": ["2026 4 9 16 11 1-1"]
}
```

**Interrupt hotkey**: `Ctrl+Alt+Q` sets `hotkey_pressed = True` via the `keyboard` library global hook. Sending loops should check this flag to stop mid-process.

### module.py — ClockThread & Widgets

`ClockThread(QThread)` polls every second and fires scheduled tasks within a 60-second execution window (prevents duplicate fires). It also drives the anti-auto-logout feature (triggers every 60 minutes). It emits `error_signal` when a scheduled task fails.

Custom widgets: `MyListWidget` (double-click to edit), `MySpinBox`, `MyDoubleSpinBox`, `MultiInputDialog`, `FileDialog`.

### wechat_locale.py — Internationalization

`WeChatLocale` maps UI element names to localized strings for zh-CN, zh-TW, and en-US WeChat clients. Required when locating controls by name.

### clipboard.py — File Clipboard

`setClipboardFiles(paths)` uses the Windows `win32clipboard` API with a DROPFILES structure to stage files for Ctrl+V sending. **Known bug**: line 22 references undefined variable `matedata` (should be `metadata`).

## Data Formats

**Message strings** (stored in config and displayed in list widgets):
- Text: `{rank}:text:{to}:{at_names}:{content}`
- File: `{rank}:file:{to}:{path}`
- `to` = `"all"` or comma-separated contact indices (`"1,2,3"`)
- `content` supports `\n` for newlines

**Schedule strings**: `{year} {month} {day} {hour} {min} {start}-{end}`
- `start-end` = message index range to send (1-based)

**Bulk TXT loading**:
- Users: one contact name per line
- Content: `all:message` or `1,2,3:message` per line (text only, no files)

## Common Pitfalls

1. **WeChat UI updates break hardcoded depths**: Re-run `automation.py` on the live WeChat window to find new control depths after any WeChat update.

2. **Do not touch WeChat launch logic**: The Ctrl+Alt+W approach (not spawning `Weixin.exe`) is a deliberate workaround for the new-login popup introduced in 2026.

3. **Clipboard timing**: The 0.3s sleeps after `pyperclip.copy()` and `setClipboardFiles()` are load-bearing. Don't remove them.

4. **`NotImplementedError` methods**: Calling `check_new_msg()`, `get_dialogs()`, `save_dialog_pictures()`, or `get_dialogs_by_time_blocks()` will raise immediately — they are not stubs with silent fallbacks.

5. **Backup files**: `ui_auto_wechat-4.0备份.py`, `gui_cp.py`, `module_cp.py` are historical backups, not active code.

## Code Conventions

- Chinese comments and variable names are mixed with English throughout.
- Error handling is minimal; high-level `try/except` catches most failures.
- GUI layouts are built programmatically with `QVBoxLayout`/`QHBoxLayout` — no `.ui` files or Qt Designer.
- No unit tests exist.
