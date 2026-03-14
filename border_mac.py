import tkinter as tk
from tkinter import ttk, colorchooser
import keyboard
import colorsys
import json
import os
import sys


class BorderApp:
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.active = False
        self.hue = 0.0
        self.is_rgb = False
        self.speed = 0.003
        self.segments = 100

        # 默认属性
        self.params = {
            "width": "60", "color": "#FFFF00",
            "font_size": "25", "font_color": "#FF0000",
            "text_tl": "", "text_tr": "", "text_bl": "", "text_br": ""
        }

        # 配置文件名
        self.config_file = "border_config.json"
        self.load_config_from_file()
        self.setup_border_ui()

    def load_config_from_file(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "params" in data:
                        self.params.update(data["params"])
                    self.is_rgb = data.get("is_rgb", False)
                    self.speed = data.get("speed", 0.003)
            except Exception as e:
                print(f"读取配置失败: {e}")

    def save_config_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "params": self.params,
                    "is_rgb": self.is_rgb,
                    "speed": self.speed
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存失败: {e}")

    def setup_border_ui(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.9)
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")

        # --- 针对 macOS 的核心透明逻辑 ---
        self.root.attributes("-transparent", True)
        self.root.config(bg='systemTransparent')
        self.canvas = tk.Canvas(self.root, bg="systemTransparent", highlightthickness=0, bd=0)

        self.canvas.pack(fill="both", expand=True)
        self.root.withdraw()
        self.animate_loop()

    def draw_elements(self):
        if not self.root or not self.active: return
        self.canvas.delete("all")

        try:
            w = int(''.join(filter(str.isdigit, str(self.params["width"]))))
            f_size = int(''.join(filter(str.isdigit, str(self.params["font_size"]))))
        except:
            w, f_size = 60, 25

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
                    rgb = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
                    color = '#%02x%02x%02x' % tuple(int(x * 255) for x in rgb)
                    self.canvas.create_line(px1, py1, px2, py2, fill=color, width=w, capstyle="butt")
                    idx += 1
        else:
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2, outline=self.params["color"],
                                         width=w)

        f_style = ("Heiti SC", f_size, "bold")  # 适配 Mac 字体
        offset = w + 20
        pos = [("text_tl", "nw", offset, offset), ("text_tr", "ne", self.sw - offset, offset),
               ("text_bl", "sw", offset, self.sh - offset), ("text_br", "se", self.sw - offset, self.sh - offset)]
        for k, a, x, y in pos:
            t = self.params[k].strip()
            if t: self.canvas.create_text(x, y, text=t, fill=self.params["font_color"], font=f_style, anchor=a)

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
            self.root.deiconify();
            self.active = True;
            self.draw_elements()
        else:
            self.root.withdraw();
            self.active = False


class SettingsPanel:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("屏幕助手 (macOS版)")
        self.win.geometry("400x750")

        self.app = BorderApp(self.win)
        self.entries = {}

        # Mac 专属快捷键
        self.hotkey = "cmd+shift+b"
        self.create_widgets()

        try:
            keyboard.add_hotkey(self.hotkey, self.app.toggle)
        except:
            print("快捷键由于 Mac 系统限制绑定失败，请手动在系统设置中授权。")

        self.win.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="macOS 专用版本", foreground="gray").pack()
        ttk.Label(frame, text=f"快捷键: ⌘ + Shift + B", font=("Arial", 12, "bold")).pack(pady=10)

        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        self.speed_scale = ttk.Scale(frame, from_=0.001, to=0.04, orient="horizontal",
                                     command=lambda v: setattr(self.app, 'speed', float(v)))
        self.speed_scale.set(self.app.speed);
        self.speed_scale.pack(fill="x", pady=10)

        self.rgb_var = tk.BooleanVar(value=self.app.is_rgb)
        ttk.Checkbutton(frame, text="开启流光特效", variable=self.rgb_var).pack()

        btn_row = ttk.Frame(frame);
        btn_row.pack(fill="x", pady=10)
        ttk.Button(btn_row, text="边框颜色", command=self.pick_b).pack(side="left", expand=True)
        ttk.Button(btn_row, text="文字颜色", command=self.pick_f).pack(side="right", expand=True)

        labels = {"text_tl": "左上文字", "text_tr": "右上文字", "text_bl": "左下文字", "text_br": "右下文字"}
        for key, text in labels.items():
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=text, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)

        ttk.Button(frame, text="👁️ 开关边框 (Mac 点击此处)", command=self.app.toggle).pack(fill="x", pady=2)
        ttk.Button(frame, text="✅ 保存并固定设置", command=self.apply).pack(fill="x", pady=10)
        ttk.Button(frame, text="❌ 退出程序", command=self.win.destroy).pack(fill="x")

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["color"] = c; self.rgb_var.set(False); self.apply()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["font_color"] = c; self.apply()

    def apply(self):
        for k, e in self.entries.items():
            self.app.params[k] = e.get()
        self.app.is_rgb = self.rgb_var.get()
        self.app.draw_elements()
        self.app.save_config_to_file()


if __name__ == "__main__":
    SettingsPanel()