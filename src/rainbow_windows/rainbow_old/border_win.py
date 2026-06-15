import tkinter as tk
from tkinter import ttk, colorchooser
import keyboard
import colorsys
import json
import os


class BorderApp:
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.active = False
        self.hue = 0.0
        self.is_rgb = False
        self.speed = 0.003
        self.segments = 100

        # 1. 预设默认属性（如果搜不到文件就用这些）
        self.params = {
            "width": "60", "color": "#FFFF00",
            "font_size": "25", "font_color": "#FF0000",
            "text_tl": "", "text_tr": "", "text_bl": "", "text_br": ""
        }

        # 配置文件名，放在同一目录下
        self.config_file = "t内容.json"

        # 2. 启动时自动搜索并加载文件
        self.load_config_from_file()

        self.setup_border_ui()

    def load_config_from_file(self):
        """核心功能：搜索并读取配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 将文件里的内容覆盖到当前内存属性中
                    if "params" in data:
                        self.params.update(data["params"])
                    self.is_rgb = data.get("is_rgb", False)
                    self.speed = data.get("speed", 0.003)
                print(f"成功加载配置文件: {self.config_file}")
            except Exception as e:
                print(f"文件读取出错，已跳过: {e}")
        else:
            print("未找到配置文件，将使用默认属性运行。")

    def save_config_to_file(self):
        """将当前属性固定到文件中"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "params": self.params,
                    "is_rgb": self.is_rgb,
                    "speed": self.speed
                }, f, ensure_ascii=False, indent=4)
            print("属性已成功固定到文件。")
        except Exception as e:
            print(f"保存失败: {e}")

    def setup_border_ui(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-transparentcolor", "#010101", "-alpha", 0.9)
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")

        self.canvas = tk.Canvas(self.root, bg="#010101", highlightthickness=0, bd=0)
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

        # 四边交叉铺满算法（无圆角，确保角部没空白）
        edges = [
            (0, w / 2, self.sw, w / 2),  # 顶
            (self.sw - w / 2, 0, self.sw - w / 2, self.sh),  # 右
            (self.sw, self.sh - w / 2, 0, self.sh - w / 2),  # 底
            (w / 2, self.sh, w / 2, 0)  # 左
        ]

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

        # 文字绘制
        f_style = ("Microsoft YaHei", f_size, "bold")
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
        self.win.title("屏幕助手 - 属性固定版")
        self.win.geometry("400x700")

        self.app = BorderApp(self.win)
        self.entries = {}
        self.create_widgets()

        keyboard.add_hotkey('f9', self.app.toggle)
        self.win.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        # 输入框部分（自动填入已加载的属性）
        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        ttk.Label(frame, text="✨ 流光速度:").pack(pady=(15, 0), anchor="w")
        self.speed_scale = ttk.Scale(frame, from_=0.001, to=0.04, orient="horizontal", command=self.update_speed)
        self.speed_scale.set(self.app.speed);
        self.speed_scale.pack(fill="x", pady=5)

        self.rgb_var = tk.BooleanVar(value=self.app.is_rgb)
        ttk.Checkbutton(frame, text="🌈 开启极光流光", variable=self.rgb_var).pack(pady=10)

        row_btn = ttk.Frame(frame);
        row_btn.pack(fill="x", pady=5)
        ttk.Button(row_btn, text="🎨 固定颜色", command=self.pick_b).pack(side="left", expand=True, padx=2)
        ttk.Button(row_btn, text="✍ 文字颜色", command=self.pick_f).pack(side="right", expand=True, padx=2)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)

        # 文字内容输入框
        labels = {"text_tl": "左上文字", "text_tr": "右上文字", "text_bl": "左下文字", "text_br": "右下文字"}
        for key, text in labels.items():
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=text, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 应用并保存
        ttk.Button(frame, text="✅ 应用设置并固定到文件", command=self.apply).pack(pady=25)
        ttk.Button(frame, text="❌ 退出程序", command=self.win.destroy).pack()
        ttk.Label(frame, text="提示：删掉 border_config.json 即可重置", foreground="gray").pack()

    def update_speed(self, val):
        self.app.speed = float(val)

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["color"] = c; self.rgb_var.set(False); self.apply()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["font_color"] = c; self.apply()

    def apply(self):
        # 从界面抓取数据
        for k, e in self.entries.items():
            self.app.params[k] = e.get()
        self.app.is_rgb = self.rgb_var.get()

        # 刷新显示
        self.app.draw_elements()
        # 核心：保存到本地文件
        self.app.save_config_to_file()


if __name__ == "__main__":
    SettingsPanel()