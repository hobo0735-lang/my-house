import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import keyboard
import colorsys
import json
import os


# --- 边框窗口逻辑类 ---
class BorderApp:
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.active = False
        self.hue = 0.0
        self.is_rgb = False
        self.speed = 0.003
        self.segments = 100

        # 默认属性 (Mac 建议用 cmd+shift+b 避免与系统 F9 冲突)
        self.params = {
            "width": "40", "color": "#FFFF00",
            "font_size": "20", "font_color": "#FF0000",
            "text_tl": "", "text_tr": "", "text_bl": "", "text_br": "",
            "hotkey": "cmd+shift+b"
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
        # --- Mac 核心适配：窗口属性 ---
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 1.0)  # 整体不透明度
        self.root.config(bg='systemTransparent')  # 关键：Mac 系统透明背景

        # 强制置顶级别，确保盖住 Dock 和全屏应用
        try:
            self.root.tk.call('wm', 'attributes', self.root._w, '-level', 'floating')
        except:
            pass

        # 获取屏幕尺寸 (Retina 屏自动处理)
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")

        # 画布透明设置
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
            w, f_size = 40, 20

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
                    self.canvas.create_line(px1, py1, px2, py2, fill=color, width=w, capstyle="butt")
                    idx += 1
        else:
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2,
                                         outline=self.params["color"], width=w)

        # Mac 默认高清字体
        f_style = ("PingFang SC", f_size, "bold")
        offset = w + 15
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
        self.win.title("屏幕助手 - macOS全功能适配版")
        self.win.geometry("400x820")
        self.app = BorderApp(self.win)
        self.entries = {}
        self.create_widgets()

        # 启动快捷键监听 (Mac需手动授权辅助功能)
        self.bind_hotkey()
        self.win.mainloop()

    def bind_hotkey(self):
        keyboard.unhook_all()
        target = self.app.params.get("hotkey", "cmd+shift+b").lower()
        try:
            keyboard.add_hotkey(target, self.app.toggle)
            print(f"成功绑定快捷键: {target}")
        except Exception as e:
            print(f"快捷键绑定失败: {e}")

    def create_widgets(self):
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        # 1. 快捷键
        hk_row = ttk.Frame(frame)
        hk_row.pack(fill="x", pady=(0, 5))
        ttk.Label(hk_row, text="⌨ 唤醒快捷键:").pack(side="left")
        self.hk_entry = ttk.Entry(hk_row)
        self.hk_entry.insert(0, self.app.params.get("hotkey", "cmd+shift+b"))
        self.hk_entry.pack(side="right", expand=True, fill="x")
        ttk.Label(frame, text="提示: Mac建议用 cmd+shift+b", foreground="gray", font=("", 10)).pack(pady=(0, 10))

        # 2. 基础属性
        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # 3. 流光速度
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

        # 4. 文字内容
        labels = {"text_tl": "左上文字", "text_tr": "右上文字", "text_bl": "左下文字", "text_br": "右下文字"}
        for key, text in labels.items():
            row = ttk.Frame(frame);
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=text, width=12).pack(side="left")
            ent = ttk.Entry(row);
            ent.insert(0, self.app.params[key]);
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        ttk.Button(frame, text="✅ 应用并保存", command=self.apply).pack(pady=20)
        ttk.Button(frame, text="❌ 退出程序", command=self.win.destroy).pack()

    def update_speed(self, val):
        self.app.speed = float(val)

    def pick_b(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["color"] = c; self.rgb_var.set(False); self.apply()

    def pick_f(self):
        c = colorchooser.askcolor()[1]
        if c: self.app.params["font_color"] = c; self.apply()

    def apply(self):
        # 动态更新快捷键
        new_hk = self.hk_entry.get().strip().lower()
        if new_hk != self.app.params["hotkey"]:
            self.app.params["hotkey"] = new_hk
            self.bind_hotkey()

        for k, e in self.entries.items(): self.app.params[k] = e.get()
        self.app.is_rgb = self.rgb_var.get()
        self.app.draw_elements()
        self.app.save_config_to_file()
        messagebox.showinfo("成功", "Mac 设置已固定并生效！")


if __name__ == "__main__":
    SettingsPanel()