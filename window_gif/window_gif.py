import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import json
import math


class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("桌宠控制台")

        self.path_var = tk.StringVar()

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=5, pady=5)

        self.entry = tk.Entry(top_frame, textvariable=self.path_var, width=35)
        self.entry.pack(side="left", padx=(0, 5))

        browse_btn = tk.Button(top_frame, text="浏览", command=self.browse_gif)
        browse_btn.pack(side="left", padx=(0, 5))

        apply_btn = tk.Button(top_frame, text="应用", command=self.apply_gif)
        apply_btn.pack(side="left", padx=(0, 5))

        min_btn = tk.Button(top_frame, text="最小化", command=self.minimize)
        min_btn.pack(side="left", padx=(10, 5))

        quit_btn = tk.Button(top_frame, text="退出", command=self.quit)
        quit_btn.pack(side="left")

        self.pet_window = tk.Toplevel(self.root)
        self.pet_window.overrideredirect(True)
        self.pet_window.attributes("-topmost", True)
        self.pet_window.configure(bg="#00ff01")
        try:
            self.pet_window.wm_attributes("-transparentcolor", "#00ff01")
        except tk.TclError:
            pass

        self.pet_label = tk.Label(self.pet_window, bg="#00ff01")
        self.pet_label.pack()

        self.pet_label.bind("<ButtonPress-1>", self.start_move)
        self.pet_label.bind("<ButtonRelease-1>", self.end_move)
        self.pet_label.bind("<B1-Motion>", self.do_move)

        self.menu = tk.Menu(self.pet_window, tearoff=0)
        self.size_menu = tk.Menu(self.menu, tearoff=0)
        for p in [25, 50, 75, 100, 150, 200]:
            self.size_menu.add_command(label=f"{p}%", command=lambda v=p: self.set_scale_percent(v))
        self.size_menu.add_separator()
        self.size_menu.add_command(label="自定义...", command=self.custom_scale)
        self.menu.add_cascade(label="调整大小", menu=self.size_menu)
        self.menu.add_separator()
        self.menu.add_command(label="更换对象", command=self.browse_gif)
        self.menu.add_command(label="退出", command=self.quit)
        self.pet_label.bind("<Button-3>", self.show_menu)

        self.original_frames = []
        self.frames = []
        self.current_frame = 0
        self.anim_after_id = None
        self.paused = False
        self.scale_percent = 100

        self.config_path = os.path.join(os.getcwd(), "desktop_pet_config.json")

        self.center_on_screen()
        self.center_pet_on_screen()
        self.load_last_gif()

    def center_on_screen(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

    def center_pet_on_screen(self):
        self.pet_window.update_idletasks()
        w = self.pet_window.winfo_width()
        h = self.pet_window.winfo_height()
        sw = self.pet_window.winfo_screenwidth()
        sh = self.pet_window.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.pet_window.geometry(f"+{x}+{y}")

    def browse_gif(self):
        path = filedialog.askopenfilename(
            title="选择 GIF 桌宠",
            filetypes=[("GIF 图片", "*.gif"), ("所有文件", "*.*")]
        )
        if path:
            self.path_var.set(path)
            self.apply_gif()

    def apply_gif(self):
        path = self.path_var.get().strip()
        if not path:
            return
        self.load_gif(path)

    def load_gif(self, path):
        if self.anim_after_id is not None:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None

        frames = []
        i = 0
        try:
            while True:
                frame = tk.PhotoImage(file=path, format=f"gif -index {i}")
                frames.append(frame)
                i += 1
        except tk.TclError:
            pass

        if not frames:
            messagebox.showerror("错误", "无法加载 GIF，请检查文件路径和格式。")
            return

        self.original_frames = frames
        self.current_frame = 0
        self.save_last_gif(path)
        self.apply_scale_to_frames()
        self.update_frame()

    def update_frame(self):
        if not self.frames:
            return
        if self.paused:
            self.anim_after_id = self.root.after(80, self.update_frame)
            return
        frame = self.frames[self.current_frame]
        self.pet_label.configure(image=frame)
        self.pet_label.image = frame
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.anim_after_id = self.root.after(80, self.update_frame)

    def minimize(self):
        self.root.iconify()

    def quit(self):
        if self.anim_after_id is not None:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None
        self.pet_window.destroy()
        self.root.destroy()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def start_move(self, event):
        self.paused = True
        self.start_x = event.x
        self.start_y = event.y

    def end_move(self, event):
        self.paused = False

    def do_move(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        x = self.pet_window.winfo_x() + dx
        y = self.pet_window.winfo_y() + dy
        self.pet_window.geometry(f"+{x}+{y}")

    def apply_scale_to_frames(self):
        if not self.original_frames:
            return
        percent = self.scale_percent
        if percent <= 0:
            percent = 100
        ratio_n = percent
        ratio_d = 100
        g = math.gcd(ratio_n, ratio_d)
        zoom = ratio_n // g
        subsample = ratio_d // g
        scaled_frames = []
        for frame in self.original_frames:
            if zoom == 1 and subsample == 1:
                scaled_frames.append(frame)
            else:
                scaled_frames.append(frame.zoom(zoom, zoom).subsample(subsample, subsample))
        self.frames = scaled_frames

    def set_scale_percent(self, percent):
        if percent < 10:
            percent = 10
        if percent > 200:
            percent = 200
        self.scale_percent = percent
        if not self.original_frames:
            return
        if self.anim_after_id is not None:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None
        self.current_frame = 0
        self.apply_scale_to_frames()
        self.update_frame()

    def custom_scale(self):
        value = simpledialog.askinteger(
            "调整大小",
            "请输入缩放百分比 (10-200):",
            minvalue=10,
            maxvalue=200,
            parent=self.pet_window,
        )
        if value is None:
            return
        self.set_scale_percent(value)

    def save_last_gif(self, path):
        data = {"last_gif": path}
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError:
            pass

    def load_last_gif(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return
        path = data.get("last_gif", "")
        if not path:
            return
        if not os.path.exists(path):
            return
        self.path_var.set(path)
        self.load_gif(path)

    def run(self):
        self.root.mainloop()


pet = DesktopPet()
pet.run()

