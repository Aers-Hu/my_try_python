import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox


class ScriptRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python脚本启动器")
        self.root.geometry("600x200")

        self.script_path = tk.StringVar()
        self.process = None
        self.lock = threading.Lock()

        frame_top = tk.Frame(self.root)
        frame_top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        label_title = tk.Label(frame_top, text="当前选择的脚本：")
        label_title.pack(anchor="w")

        self.label_path = tk.Label(frame_top, textvariable=self.script_path, anchor="w", fg="blue", wraplength=560)
        self.label_path.pack(fill=tk.X, pady=5)

        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(fill=tk.X, padx=10, pady=10)

        btn_select = tk.Button(frame_buttons, text="选择脚本", width=12, command=self.choose_script)
        btn_select.grid(row=0, column=0, padx=5)

        self.btn_start = tk.Button(frame_buttons, text="开始执行", width=12, command=self.start_script, state=tk.DISABLED)
        self.btn_start.grid(row=0, column=1, padx=5)

        self.btn_stop = tk.Button(frame_buttons, text="停止执行", width=12, command=self.stop_script, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=2, padx=5)

        btn_change = tk.Button(frame_buttons, text="更改脚本", width=12, command=self.change_script)
        btn_change.grid(row=0, column=3, padx=5)

        btn_minimize = tk.Button(frame_buttons, text="最小化", width=12, command=self.minimize_window)
        btn_minimize.grid(row=1, column=1, padx=5, pady=5)

        btn_exit = tk.Button(frame_buttons, text="退出程序", width=12, command=self.exit_app)
        btn_exit.grid(row=1, column=2, padx=5, pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def choose_script(self):
        file_path = filedialog.askopenfilename(
            title="选择要执行的Python脚本",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        self.script_path.set(file_path)
        self.update_button_states()

    def change_script(self):
        if self.process is not None:
            result = messagebox.askyesno("更改脚本", "当前有脚本在运行，是否先停止再更改？")
            if result:
                self.stop_script()
        self.choose_script()

    def start_script(self):
        with self.lock:
            if self.process is not None:
                messagebox.showinfo("提示", "已有脚本在运行，请先停止当前脚本。")
                return
            script = self.script_path.get()
            if not script:
                messagebox.showwarning("警告", "请先选择要执行的脚本。")
                return
            if not os.path.isfile(script):
                messagebox.showerror("错误", "脚本文件不存在。")
                return

            python_cmd = self.get_python_command()
            try:
                self.process = subprocess.Popen(
                    [python_cmd, script],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            except Exception as e:
                self.process = None
                messagebox.showerror("错误", f"启动脚本失败：{e}")
                return

        self.update_button_states()
        threading.Thread(target=self._watch_process, daemon=True).start()

    def _watch_process(self):
        if self.process is None:
            return
        self.process.wait()
        with self.lock:
            self.process = None
        self.root.after(0, self.update_button_states)

    def stop_script(self):
        with self.lock:
            if self.process is None:
                return
            try:
                self.process.terminate()
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.update_button_states()

    def minimize_window(self):
        self.root.iconify()

    def exit_app(self):
        self.stop_script()
        self.root.destroy()

    def update_button_states(self):
        script_selected = bool(self.script_path.get())
        running = self.process is not None
        if script_selected and not running:
            self.btn_start.configure(state=tk.NORMAL)
        else:
            self.btn_start.configure(state=tk.DISABLED)
        if running:
            self.btn_stop.configure(state=tk.NORMAL)
        else:
            self.btn_stop.configure(state=tk.DISABLED)

    def get_python_command(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable


def main():
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
