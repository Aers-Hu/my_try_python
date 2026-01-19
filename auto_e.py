import keyboard
import time
from threading import Event

# 控制变量
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

# 设置全局热键
keyboard.add_hotkey('f1', toggle_run)      # F1 启动/停止
keyboard.add_hotkey('f2', toggle_pause)    # F2 暂停/继续
keyboard.add_hotkey('f3', stop_script)     # F3 退出程序

print("""自动输入E键脚本已就绪
控制命令:
F1 - 启动/停止
F2 - 暂停/继续
F3 - 退出程序
""")

try:
    while not exit_event.is_set():
        if running and not paused:
            keyboard.press_and_release('e')
            print(f"已输入E - {time.strftime('%H:%M:%S')}")
        
        # 等待3秒，但每秒检查一次退出事件
        for _ in range(3):
            if exit_event.is_set():
                break
            time.sleep(1)
            
except KeyboardInterrupt:
    print("\n用户中断脚本")
finally:
    keyboard.unhook_all()
    print("脚本已安全退出")

