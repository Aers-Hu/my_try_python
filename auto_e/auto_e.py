import tkinter as tk
from tkinter import messagebox
import keyboard
import time
import threading
import sys
import logging
from threading import Event

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='auto_press.log'
)

# 配置项
KEY_TO_PRESS = 'e'
INTERVAL = 1.5
START_STOP_KEY = 'f1'
PAUSE_KEY = 'f2'
EXIT_KEY = 'f3'

# 状态变量
running = False
paused = False
exit_event = Event()

# Windows API 检测
try:
    import win32api
    import win32con
    HAS_WIN32API = True
except ImportError:
    HAS_WIN32API = False

# GUI 初始化
root = tk.Tk()
root.withdraw()
messagebox.showinfo("自动按键脚本", f"✅ 脚本已启动！\n\n控制命令:\n{START_STOP_KEY.upper()} - 启动/停止\n{PAUSE_KEY.upper()} - 暂停/继续\n{EXIT_KEY.upper()} - 退出")

def press_key():
    try:
        if HAS_WIN32API and KEY_TO_PRESS.isalpha():
            win32api.keybd_event(ord(KEY_TO_PRESS.upper()), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord(KEY_TO_PRESS.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            keyboard.press(KEY_TO_PRESS)
            time.sleep(0.05)
            keyboard.release(KEY_TO_PRESS)
        logging.debug(f"已按下 {KEY_TO_PRESS}")
    except Exception as e:
        logging.error(f"按键错误: {e}")

def key_press_worker():
    while not exit_event.is_set():
        if running and not paused:
            press_key()
            time.sleep(INTERVAL)
        else:
            time.sleep(0.1)

def toggle_run():
    global running
    running = not running
    logging.info(f"脚本 {'启动' if running else '停止'}")

def toggle_pause():
    global paused
    paused = not paused
    logging.info(f"脚本 {'暂停' if paused else '继续'}")

def stop_script():
    global running, paused
    running = False
    paused = False
    exit_event.set()
    logging.info("脚本退出")
    keyboard.unhook_all()
    root.quit()
    sys.exit(0)

# 启动线程
key_thread = threading.Thread(target=key_press_worker, daemon=True)
key_thread.start()

# 注册热键
keyboard.add_hotkey(START_STOP_KEY, toggle_run)
keyboard.add_hotkey(PAUSE_KEY, toggle_pause)
keyboard.add_hotkey(EXIT_KEY, stop_script)

logging.info(f"""脚本已就绪
模拟按键: {KEY_TO_PRESS}
间隔: {INTERVAL}秒
热键: 
{START_STOP_KEY.upper()}-启动/停止 
{PAUSE_KEY.upper()}-暂停/继续 
{EXIT_KEY.upper()}-退出""")

try:
    root.mainloop()  # 保持GUI运行
except Exception as e:
    logging.critical(f"致命错误: {e}")
finally:
    stop_script()
