import tkinter as tk
from tkinter import ttk, colorchooser
import keyboard
import threading
import colorsys


class BorderApp:
    def __init__(self):
        self.root = None
        self.active = False
        self.hue = 0.0
        self.is_rgb = False
        self.segments = 50  # 每一条边的分段数，越多过渡越细腻
        self.speed = 0.003  # 预设的优雅慢速
        self.params = {
            "width": "60", "color": "#FFFF00",
            "font_size": "25", "font_color": "#FF0000",
            "text_tl": "", "text_tr": "", "text_bl": "", "text_br": ""
        }

    def setup_border_ui(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        # 透明色设为 #010101
        self.root.attributes("-topmost", True, "-transparentcolor", "#010101", "-alpha", 0.9)
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.canvas = tk.Canvas(self.root, bg="#010101", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_elements()
        self.root.withdraw()
        self.animate_loop()
        self.root.mainloop()

    def draw_elements(self):
        """高级感流光绘图核心"""
        if not self.root: return
        self.canvas.delete("all")

        try:
            w = int(''.join(filter(str.isdigit, str(self.params["width"]))))
            f_size = int(''.join(filter(str.isdigit, str(self.params["font_size"]))))
        except:
            w, f_size = 60, 25

        if self.is_rgb:
            # 定义四条边的轨迹
            edges = [
                (w / 2, w / 2, self.sw - w / 2, w / 2),  # 顶
                (self.sw - w / 2, w / 2, self.sw - w / 2, self.sh - w / 2),  # 右
                (self.sw - w / 2, self.sh - w / 2, w / 2, self.sh - w / 2),  # 底
                (w / 2, self.sh - w / 2, w / 2, w / 2)  # 左
            ]

            seg_idx = 0
            for x1, y1, x2, y2 in edges:
                for i in range(self.segments):
                    p1_x = x1 + (x2 - x1) * i / self.segments
                    p1_y = y1 + (y2 - y1) * i / self.segments
                    p2_x = x1 + (x2 - x1) * (i + 1) / self.segments
                    p2_y = y1 + (y2 - y1) * (i + 1) / self.segments

                    # --- 高级色算法 ---
                    # 色相偏移：分母 300 让颜色跨度更大更优雅
                    current_hue = (self.hue + (seg_idx / 300)) % 1.0

                    # 配方：S=0.65(柔和), V=0.95(明亮但不刺眼)
                    rgb = colorsys.hsv_to_rgb(current_hue, 0.65, 0.95)
                    color = '#%02x%02x%02x' % tuple(int(x * 255) for x in rgb)

                    self.canvas.create_line(p1_x, p1_y, p2_x, p2_y, fill=color, width=w)
                    seg_idx += 1
        else:
            # 静态模式
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2, outline=self.params["color"],
                                         width=w)

        # 文字绘制
        f_conf = ("Microsoft YaHei", f_size, "bold")
        offset = w + 20
        for key, anchor, x, y in [("text_tl", "nw", offset, offset), ("text_tr", "ne", self.sw - offset, offset),
                                  ("text_bl", "sw", offset, self.sh - offset),
                                  ("text_br", "se", self.sw - offset, self.sh - offset)]:
            txt = self.params[key].strip()
            if txt: self.canvas.create_text(x, y, text=txt, fill=self.params["font_color"], font=f_conf, anchor=anchor)

    def animate_loop(self):
        if self.active and self.is_rgb:
            self.hue -= self.speed
            self.draw_elements()
            ms = 50  # 维持丝滑帧率
        else:
            ms = 300
        self.root.after(ms, self.animate_loop)

    def toggle(self):
        if self.root:
            if not self.active:
                self.root.deiconify()
                self.active = True
                self.draw_elements()
            else:
                self.root.withdraw()
                self.active = False


class SettingsPanel:
    def __init__(self, border_app):
        self.app = border_app
        self.win = tk.Tk()
        self.win.title("屏幕助手 - 极光高级定制版")
        self.win.geometry("400x700")
        self.entries = {}
        self.create_widgets()
        self.win.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        # 基础设置
        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 速度调节滑块
        ttk.Label(frame, text="✨ 流光速度 (往左调更高级):").pack(pady=(15, 0), anchor="w")
        self.speed_scale = ttk.Scale(frame, from_=0.001, to=0.04, orient="horizontal", command=self.update_speed)
        self.speed_scale.set(self.app.speed)
        self.speed_scale.pack(fill="x", pady=5)

        # 流光开关
        self.rgb_check = ttk.Checkbutton(frame, text="🌈 开启极光渐变流光")
        self.rgb_check.pack(pady=10)
        if self.app.is_rgb: self.rgb_check.state(['selected'])

        # 颜色选择
        row_btn = ttk.Frame(frame);
        row_btn.pack(fill="x", pady=5)
        ttk.Button(row_btn, text="🎨 固定边框颜色", command=self.pick_b).pack(side="left", expand=True, padx=2)
        ttk.Button(row_btn, text="✍ 文字颜色", command=self.pick_f).pack(side="right", expand=True, padx=2)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)

        # 文字内容
        labels = {"text_tl": "左上文字", "text_tr": "右上文字", "text_bl": "左下文字", "text_br": "右下文字"}
        for key, label_text in labels.items():
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label_text, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 应用按钮
        ttk.Button(frame, text="✅ 立即应用并刷新屏幕", command=self.apply).pack(pady=25)
        ttk.Label(frame, text="快捷键: F9 开关", foreground="gray").pack()

    def update_speed(self, val):
        self.app.speed = float(val)

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.app.params["color"] = c
            self.rgb_check.state(['!selected'])
            self.app.is_rgb = False
            self.app.draw_elements()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.app.params["font_color"] = c
            self.app.draw_elements()

    def apply(self):
        # 强制抓取所有文本和物理勾选状态
        for k, e in self.entries.items():
            self.app.params[k] = e.get()
        self.app.is_rgb = 'selected' in self.rgb_check.state()
        self.app.draw_elements()
        print(f">>> 设置已更新！流光模式: {self.app.is_rgb}, 速度: {self.app.speed:.4f}")


if __name__ == "__main__":
    border_instance = BorderApp()
    threading.Thread(target=border_instance.setup_border_ui, daemon=True).start()
    keyboard.add_hotkey('f9', border_instance.toggle)
    SettingsPanel(border_instance)