import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import keyboard
import colorsys
import json
import os


class BorderApp:
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.active = False
        self.hue = 0.0
        self.active_corner = "tl"

        # 初始参数
        self.params = {
            "width": "60",
            "color": "#FFFF00",
            "font_size": "30",
            "font_color": "#FFFFFF",
            "hotkey": "f9",
            "prev_key": "page up",
            "next_key": "page down",
            "is_rgb": True,
            "speed_level": 30,  # 滑动条刻度 1-100
            "library": ["初衷不变", "岁月如歌", "兄弟挺你", "班会往事", "坦诚相待"],
            "indices": {"tl": 0, "tr": 0, "bl": 0, "br": 0}
        }

        self.config_file = "t内容.json"
        self.load_config_from_file()
        self.setup_border_ui()
        self.register_custom_hotkeys()

    def load_config_from_file(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.params.update(data)
            except:
                pass

    def save_config_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.params, f, ensure_ascii=False, indent=4)
        except:
            pass

    def setup_border_ui(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-transparentcolor", "#010101", "-alpha", 0.9)
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.canvas = tk.Canvas(self.root, bg="#010101", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.root.withdraw()
        self.animate_loop()

    def handle_click(self, event):
        if event.x < self.sw / 2 and event.y < self.sh / 2:
            self.active_corner = "tl"
        elif event.x >= self.sw / 2 and event.y < self.sh / 2:
            self.active_corner = "tr"
        elif event.x < self.sw / 2 and event.y >= self.sh / 2:
            self.active_corner = "bl"
        else:
            self.active_corner = "br"
        self.draw_elements()

    def register_custom_hotkeys(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey(self.params["hotkey"], self.toggle)
            keyboard.add_hotkey(self.params["prev_key"], lambda: self.switch_content(-1))
            keyboard.add_hotkey(self.params["next_key"], lambda: self.switch_content(1))
        except:
            pass

    def switch_content(self, direction):
        if not self.active: return
        lib = self.params["library"]
        curr_idx = self.params["indices"][self.active_corner]
        self.params["indices"][self.active_corner] = (curr_idx + direction) % len(lib)
        self.draw_elements()
        self.save_config_to_file()

    def draw_elements(self):
        if not self.root or not self.active: return
        self.canvas.delete("all")
        w = int(self.params["width"])
        f_size = int(self.params["font_size"])

        if self.params["is_rgb"]:
            segments = 80
            edges = [(0, w / 2, self.sw, w / 2), (self.sw - w / 2, 0, self.sw - w / 2, self.sh),
                     (self.sw, self.sh - w / 2, 0, self.sh - w / 2), (w / 2, self.sh, w / 2, 0)]
            idx = 0
            for x1, y1, x2, y2 in edges:
                for i in range(segments):
                    px1, py1 = x1 + (x2 - x1) * i / segments, y1 + (y2 - y1) * i / segments
                    px2, py2 = x1 + (x2 - x1) * (i + 1) / segments, y1 + (y2 - y1) * (i + 1) / segments
                    hue = (self.hue + (idx / 320)) % 1.0
                    color = '#%02x%02x%02x' % tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.65, 0.95))
                    self.canvas.create_line(px1, py1, px2, py2, fill=color, width=w)
                    idx += 1
        else:
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2, outline=self.params["color"],
                                         width=w)

        lib, idxs, offset = self.params["library"], self.params["indices"], w + 25
        pos = [("tl", "nw", offset, offset), ("tr", "ne", self.sw - offset, offset),
               ("bl", "sw", offset, self.sh - offset), ("br", "se", self.sw - offset, self.sh - offset)]

        for key, anchor, x, y in pos:
            text = lib[idxs[key]]
            color = "#FFFF00" if key == self.active_corner else self.params["font_color"]
            self.canvas.create_text(x, y, text=text, fill=color, font=("Microsoft YaHei", f_size, "bold"),
                                    anchor=anchor)

    def animate_loop(self):
        if self.active and self.params["is_rgb"]:
            # 内部换算：滑动条 1-100 映射到 0.0001 - 0.015
            level = float(self.params.get("speed_level", 30))
            real_speed = level * 0.00015
            self.hue -= real_speed
            self.draw_elements()
            ms = 40
        else:
            ms = 200
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
        self.win.title("灵魂边框 - 调速版")
        self.win.geometry("420x700")
        self.app = BorderApp(self.win)
        self.create_widgets()
        self.win.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        self.entries = {}
        fields = [("⌨ 唤醒快捷键:", "hotkey"), ("⬅ 后退翻页键:", "prev_key"),
                  ("➡ 前进翻页键:", "next_key"), ("📏 边框粗细:", "width"), ("🔠 字体大小:", "font_size")]

        for label, key in fields:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, width=15).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # --- 重点：可视化进度条调速 ---
        ttk.Label(frame, text="\n⚡ 流光旋转速度:").pack(anchor="w")
        self.speed_scale = tk.Scale(frame, from_=1, to=100, orient="horizontal",
                                    length=300, showvalue=True, tickinterval=0)
        self.speed_scale.set(self.app.params.get("speed_level", 30))
        self.speed_scale.pack(pady=10)

        self.rgb_var = tk.BooleanVar(value=self.app.params["is_rgb"])
        ttk.Checkbutton(frame, text="🌈 开启极光流光", variable=self.rgb_var).pack(pady=10)

        btn_row = ttk.Frame(frame);
        btn_row.pack(fill="x", pady=10)
        ttk.Button(btn_row, text="🎨 边框色", command=self.pick_b).pack(side="left", expand=True)
        ttk.Button(btn_row, text="✍ 文字色", command=self.pick_f).pack(side="right", expand=True)

        ttk.Button(frame, text="✅ 应用并保存", command=self.apply).pack(pady=20)
        ttk.Button(frame, text="❌ 彻底退出", command=self.win.destroy).pack()

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["color"] = c; self.app.draw_elements()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["font_color"] = c; self.app.draw_elements()

    def apply(self):
        for key, ent in self.entries.items():
            val = ent.get().strip()
            self.app.params[key] = val.lower() if "key" in key or "hotkey" in key else val

        self.app.params["speed_level"] = self.speed_scale.get()
        self.app.params["is_rgb"] = self.rgb_var.get()
        self.app.register_custom_hotkeys()
        self.app.draw_elements()
        self.app.save_config_to_file()
        messagebox.showinfo("成功", "设置已同步，速度已起飞！")


if __name__ == "__main__":
    SettingsPanel()