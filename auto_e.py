import keyboard
import time
from threading import Event
#运行脚本：python script_name.pye
import keyboard
import time
from threading import Event
import win32api
import win32con

# 配置项
KEY_TO_PRESS = 'e'  # 要模拟的按键
INTERVAL = 3.0  # 按键间隔(秒)
START_STOP_KEY = 'f1'  # 开始/停止键
PAUSE_KEY = 'f2'  # 暂停键
EXIT_KEY = 'f3'  # 退出键

# 状态变量
running = False
paused = False
exit_event = Event()


def toggle_run():
    global running
    running = not running
    print(f"脚本已 {'启动' if running else '停止'}")


def toggle_pause():
    global paused
    paused = not paused
    print(f"脚本已 {'暂停' if paused else '继续'}")


def stop_script():
    print("正在退出脚本...")
    exit_event.set()


# 更可靠的按键模拟(使用Windows API)
def press_key():
    try:
        # 方法1: 使用keyboard库(较通用)
        keyboard.press(KEY_TO_PRESS)
        time.sleep(0.05)  # 短暂按住
        keyboard.release(KEY_TO_PRESS)

        # 方法2: 使用win32api(更底层，可选)
        # win32api.keybd_event(ord(KEY_TO_PRESS), 0, 0, 0)
        # time.sleep(0.05)
        # win32api.keybd_event(ord(KEY_TO_PRESS), 0, win32con.KEYEVENTF_KEYUP, 0)

        print(f"已模拟按下 {KEY_TO_PRESS} - {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"按键模拟失败: {e}")


# 设置热键
keyboard.add_hotkey(START_STOP_KEY, toggle_run)
keyboard.add_hotkey(PAUSE_KEY, toggle_pause)
keyboard.add_hotkey(EXIT_KEY, stop_script)

print(f"""游戏按键模拟脚本已就绪
模拟按键: {KEY_TO_PRESS}
按键间隔: {INTERVAL}秒
控制命令:
{START_STOP_KEY.upper()} - 启动/停止
{PAUSE_KEY.upper()} - 暂停/继续
{EXIT_KEY.upper()} - 退出程序
""")

try:
    while not exit_event.is_set():
        if running and not paused:
            press_key()

        # 更精确的间隔控制
        start_time = time.time()
        while (time.time() - start_time) < INTERVAL and not exit_event.is_set():
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\n用户中断脚本")
finally:
    keyboard.unhook_all()
    print("脚本已安全退出")

