import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import keyboard
import colorsys
import json
import os
import platform


# --- 边框窗口逻辑类 ---
class BorderApp:
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.active = False
        self.hue = 0.0
        self.is_rgb = False
        self.speed = 0.003
        self.segments = 100
        self.active_corner = "tl"  # 当前选中的操作角

        # 默认属性
        self.params = {
            "width": "40", "color": "#FFFF00",
            "font_size": "25", "font_color": "#FFFFFF",
            "hotkey": "cmd+shift+b",
            "prev_key": "left",  # 后退键 (Mac建议方向键)
            "next_key": "right",  # 前进键
            # 词库模式核心数据
            "library": ["初衷不变", "岁月如歌", "兄弟挺你", "班会往事", "赤诚相待"],
            "indices": {"tl": 0, "tr": 0, "bl": 0, "br": 0}
        }

        self.config_file = "t内容.json"
        self.load_config_from_file()
        self.setup_border_ui()

    def load_config_from_file(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "params" in data: self.params.update(data["params"])
                    self.is_rgb = data.get("is_rgb", False)
                    self.speed = data.get("speed", 0.003)
            except:
                pass

    def save_config_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"params": self.params, "is_rgb": self.is_rgb, "speed": self.speed}, f,
                          ensure_ascii=False, indent=4)
        except:
            pass

    def setup_border_ui(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg='systemTransparent')

        # 强制置顶级别 (Mac 专用)
        try:
            self.root.tk.call('wm', 'attributes', self.root._w, '-level', 'floating')
        except:
            pass

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")

        self.canvas = tk.Canvas(self.root, bg="systemTransparent", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # 绑定点击事件：点击屏幕四角切换操作目标
        self.canvas.bind("<Button-1>", self.handle_click)

        self.root.withdraw()
        self.animate_loop()

    def handle_click(self, event):
        """判定点击位置锁定角落"""
        if event.x < self.sw / 2 and event.y < self.sh / 2:
            self.active_corner = "tl"
        elif event.x >= self.sw / 2 and event.y < self.sh / 2:
            self.active_corner = "tr"
        elif event.x < self.sw / 2 and event.y >= self.sh / 2:
            self.active_corner = "bl"
        else:
            self.active_corner = "br"
        self.draw_elements()

    def switch_content(self, direction):
        """快捷键触发的切换逻辑"""
        if not self.active: return
        lib = self.params["library"]
        if not lib: return
        curr_idx = self.params["indices"][self.active_corner]
        self.params["indices"][self.active_corner] = (curr_idx + direction) % len(lib)
        self.draw_elements()
        self.save_config_to_file()

    def draw_elements(self):
        if not self.root or not self.active: return
        self.canvas.delete("all")

        try:
            w = int(''.join(filter(str.isdigit, str(self.params["width"]))))
            f_size = int(''.join(filter(str.isdigit, str(self.params["font_size"]))))
        except:
            w, f_size = 40, 25

        # 1. 绘制流光边框
        edges = [(0, w / 2, self.sw, w / 2), (self.sw - w / 2, 0, self.sw - w / 2, self.sh),
                 (self.sw, self.sh - w / 2, 0, self.sh - w / 2), (w / 2, self.sh, w / 2, 0)]

        if self.is_rgb:
            idx = 0
            for x1, y1, x2, y2 in edges:
                for i in range(self.segments):
                    px1 = x1 + (x2 - x1) * i / self.segments
                    py1 = y1 + (y2 - y1) * i / self.segments
                    px2 = x1 + (x2 - x1) * (i + 1) / self.segments
                    py2 = y1 + (y2 - y1) * (i + 1) / self.segments
                    hue = (self.hue + (idx / 400)) % 1.0
                    color = '#%02x%02x%02x' % tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.65, 0.95))
                    self.canvas.create_line(px1, py1, px2, py2, fill=color, width=w)
                    idx += 1
        else:
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2,
                                         outline=self.params["color"], width=w)

        # 2. 绘制词库文字
        f_style = ("PingFang SC", f_size, "bold")
        offset = w + 20
        lib = self.params["library"]
        idxs = self.params["indices"]

        pos_cfg = [
            ("tl", "nw", offset, offset), ("tr", "ne", self.sw - offset, offset),
            ("bl", "sw", offset, self.sh - offset), ("br", "se", self.sw - offset, self.sh - offset)
        ]

        for key, anchor, x, y in pos_cfg:
            content = lib[idxs[key]] if lib else ""
            # 当前操作的角显示黄色，其余显示用户设定的颜色
            color = "#FFFF00" if key == self.active_corner else self.params["font_color"]
            self.canvas.create_text(x, y, text=content, fill=color, font=f_style, anchor=anchor)

    def animate_loop(self):
        if self.active and self.is_rgb:
            self.hue -= self.speed
            self.draw_elements()
            ms = 40
        else:
            ms = 400
        self.root.after(ms, self.animate_loop)

    def toggle(self):
        if not self.active:
            self.root.deiconify()
            self.active = True
            self.draw_elements()
        else:
            self.root.withdraw()
            self.active = False


# --- 设置面板类 ---
class SettingsPanel:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("屏幕助手 - Mac PPT版")
        self.win.geometry("400x750")
        self.app = BorderApp(self.win)
        self.entries = {}
        self.create_widgets()
        self.bind_hotkeys()
        self.win.mainloop()

    def bind_hotkeys(self):
        keyboard.unhook_all()
        # 绑定唤醒
        keyboard.add_hotkey(self.app.params["hotkey"], self.app.toggle)
        # 绑定翻页 (前进/后退)
        keyboard.add_hotkey(self.app.params["prev_key"], lambda: self.app.switch_content(-1))
        keyboard.add_hotkey(self.app.params["next_key"], lambda: self.app.switch_content(1))

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        # 1. 快捷键组
        keys = [("⌨ 唤醒快捷键", "hotkey"), ("⬅ 后退翻页键", "prev_key"), ("➡ 前进翻页键", "next_key")]
        for label, key in keys:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 2. 边框属性
        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 3. 流光速度
        ttk.Label(frame, text="✨ 流光旋转速度:").pack(pady=(15, 0), anchor="w")
        self.speed_scale = ttk.Scale(frame, from_=0.001, to=0.04, orient="horizontal", command=self.update_speed)
        self.speed_scale.set(self.app.speed);
        self.speed_scale.pack(fill="x", pady=5)

        self.rgb_var = tk.BooleanVar(value=self.app.is_rgb)
        ttk.Checkbutton(frame, text="🌈 开启极光流光", variable=self.rgb_var).pack(pady=10)

        # 颜色
        row_btn = ttk.Frame(frame);
        row_btn.pack(fill="x", pady=5)
        ttk.Button(row_btn, text="🎨 边框颜色", command=self.pick_b).pack(side="left", expand=True, padx=2)
        ttk.Button(row_btn, text="✍ 文字颜色", command=self.pick_f).pack(side="right", expand=True, padx=2)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(frame, text="💡 提示：在开启边框后，点击屏幕某个角\n即可锁定该角，使用方向键切换文字。",
                  foreground="gray").pack()

        ttk.Button(frame, text="✅ 应用并保存", command=self.apply).pack(pady=20)
        ttk.Button(frame, text="❌ 彻底退出", command=self.win.destroy).pack()

    def update_speed(self, val):
        self.app.speed = float(val)

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["color"] = c; self.apply()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["font_color"] = c; self.apply()

    def apply(self):
        for k, e in self.entries.items(): self.app.params[k] = e.get().lower()
        self.app.is_rgb = self.rgb_var.get()
        self.bind_hotkeys()
        self.app.draw_elements()
        self.app.save_config_to_file()
        messagebox.showinfo("成功", "Mac 设置已更新！")


if __name__ == "__main__":
    SettingsPanel()