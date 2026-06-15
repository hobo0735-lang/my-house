import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import keyboard  # 用于全局快捷键监听
import colorsys  # 用于将 HSV 颜色转换为 RGB 界面颜色
import json  # 用于保存和读取配置
import os  # 用于检查配置文件是否存在


# --- 核心逻辑类：负责全屏置顶边框的显示与动画 ---
class BorderApp:
    def __init__(self, master):
        # 1. 基础窗口属性（这里的 master 是设置面板，作为父窗口）
        self.root = tk.Toplevel(master)
        self.active = False  # 标记当前边框是否正在显示
        self.hue = 0.0  # HSV 颜色模型的色相（0.0-1.0），用于流光动画
        self.is_rgb = False  # 是否开启 RGB 流光模式
        self.speed = 0.003  # 流光颜色变换的速度
        self.segments = 100  # 将每条边细分为多少段（段数越多流光越细腻）

        # 默认参数字典：包含宽度、颜色、字体及四个角落的文字
        self.params = {
            "width": "60", "color": "#FFFF00",
            "font_size": "25", "font_color": "#FF0000",
            "text_tl": "", "text_tr": "", "text_bl": "", "text_br": "",
            "hotkey": "f9"
        }

        # 2. 尝试从本地 JSON 文件恢复上次保存的设置
        self.config_file = "t内容.json"
        self.load_config_from_file()

        # 3. 初始化边框 UI 窗口
        self.setup_border_ui()

    def load_config_from_file(self):
        """从 JSON 读取持久化数据"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "params" in data: self.params.update(data["params"])
                    self.is_rgb = data.get("is_rgb", False)
                    self.speed = data.get("speed", 0.003)
            except:
                pass  # 如果读取失败则使用默认值

    def save_config_to_file(self):
        """将当前设置保存到 JSON 文件中"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"params": self.params, "is_rgb": self.is_rgb, "speed": self.speed}, f,
                          ensure_ascii=False, indent=4)
        except:
            pass

    def setup_border_ui(self):
        """创建全屏透明、置顶、穿透的画布窗口"""
        self.root.overrideredirect(True)  # 移除窗口标题栏和边框
        self.root.attributes("-topmost", True)  # 窗口永远置顶
        # 设置透明色：将 #010101 这种颜色识别为完全透明，以此露出桌面
        self.root.attributes("-transparentcolor", "#010101")
        self.root.attributes("-alpha", 0.9)  # 整体透明度 90%

        # 获取屏幕宽高
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")

        # 创建全屏画布，背景色设为透明色
        self.canvas = tk.Canvas(self.root, bg="#010101", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.root.withdraw()  # 初始状态为隐藏
        self.animate_loop()  # 开启重绘循环

    def  draw_elements(self):
        """根据最新参数在画布上绘制边框和文字"""
        if not self.root or not self.active: return
        self.canvas.delete("all")  # 清空当前画布

        # 数据清洗：确保宽度和字号是纯数字
        try:
            w = int(''.join(filter(str.isdigit, str(self.params["width"]))))
            f_size = int(''.join(filter(str.isdigit, str(self.params["font_size"]))))
        except:
            w, f_size = 60, 25

        # 定义屏幕四条边的坐标线段（顺时针：顶、右、底、左）
        edges = [(0, w / 2, self.sw, w / 2), (self.sw - w / 2, 0, self.sw - w / 2, self.sh),
                 (self.sw, self.sh - w / 2, 0, self.sh - w / 2), (w / 2, self.sh, w / 2, 0)]

        if self.is_rgb:
            # --- 极光流光模式逻辑 ---
            idx = 0
            for x1, y1, x2, y2 in edges:
                for i in range(self.segments):
                    # 插值计算每一小段的起始和终止坐标
                    px1 = x1 + (x2 - x1) * i / self.segments
                    py1 = y1 + (y2 - y1) * i / self.segments
                    px2 = x1 + (x2 - x1) * (i + 1) / self.segments
                    py2 = y1 + (y2 - y1) * (i + 1) / self.segments

                    # 基于当前 hue 值计算颜色，idx 偏移量产生颜色渐变流动感
                    hue = (self.hue + (idx / 400)) % 1.0
                    color = '#%02x%02x%02x' % tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.65, 0.95))
                    self.canvas.create_line(px1, py1, px2, py2, fill=color, width=w, capstyle="butt")
                    idx += 1
        else:
            # --- 固定颜色模式 ---
            self.canvas.create_rectangle(w / 2, w / 2, self.sw - w / 2, self.sh - w / 2,
                                         outline=self.params["color"], width=w)

        # 绘制四个角落的文字
        f_style = ("Microsoft YaHei", f_size, "bold")
        offset = w + 20  # 文字与边框的间距
        pos = [("text_tl", "nw", offset, offset), ("text_tr", "ne", self.sw - offset, offset),
               ("text_bl", "sw", offset, self.sh - offset), ("text_br", "se", self.sw - offset, self.sh - offset)]

        for k, a, x, y in pos:
            t = self.params[k].strip()
            if t: self.canvas.create_text(x, y, text=t, fill=self.params["font_color"], font=f_style, anchor=a)

    def animate_loop(self):
        """循环动画引擎：定时刷新界面"""
        if self.active and self.is_rgb:
            self.hue -= self.speed  # 每一帧改变色相
            self.draw_elements()  # 重绘
            ms = 40  # 约 25 帧/秒
        else:
            ms = 400  # 静态模式降低功耗
        self.root.after(ms, self.animate_loop)

    def toggle(self):
        """显示或隐藏切换"""
        if not self.active:
            self.root.deiconify()  # 显示窗口
            self.active = True
            self.draw_elements()
        else:
            self.root.withdraw()  # 隐藏窗口
            self.active = False


# --- 设置面板类：负责用户交互和参数管理 ---
class SettingsPanel:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("屏幕助手 - 配置面板")
        self.win.geometry("400x780")

        # 实例化边框逻辑类
        self.app = BorderApp(self.win)
        self.entries = {}  # 存放输入框对象的字典，方便后续批量读取
        self.create_widgets()

        # 挂载全局键盘钩子，监听用户自定义的快捷键
        keyboard.hook(self.universal_handler)
        self.win.mainloop()

    def universal_handler(self, event):
        """键盘事件分发器"""
        if event.event_type == 'down':
            target = self.app.params.get("hotkey", "f9").lower()
            try:
                # 检查按下的键是否匹配设定的快捷键
                if keyboard.is_pressed(target):
                    self.app.toggle()
            except:
                pass

    def create_widgets(self):
        """创建面板上的 UI 元素"""
        frame = ttk.Frame(self.win, padding="20")
        frame.pack(fill="both", expand=True)

        # --- 快捷键设置 ---
        hk_row = ttk.Frame(frame)
        hk_row.pack(fill="x", pady=(0, 10))
        ttk.Label(hk_row, text="⌨ 唤醒快捷键:").pack(side="left")
        self.hk_entry = ttk.Entry(hk_row)
        self.hk_entry.insert(0, self.app.params.get("hotkey", "f9"))
        self.hk_entry.pack(side="right", expand=True, fill="x")

        # --- 基础数值：宽度与字号 ---
        for label, key in [("边框粗细", "width"), ("字体大小", "font_size")]:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ent = ttk.Entry(row)
            ent.insert(0, self.app.params[key])
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # --- 流光速度滑动条 ---
        ttk.Label(frame, text="✨ 流光速度:").pack(pady=(15, 0), anchor="w")
        self.speed_scale = ttk.Scale(frame, from_=0.001, to=0.04, orient="horizontal", command=self.update_speed)
        self.speed_scale.set(self.app.speed)
        self.speed_scale.pack(fill="x", pady=5)

        # --- RGB 开关 ---
        self.rgb_var = tk.BooleanVar(value=self.app.is_rgb)
        ttk.Checkbutton(frame, text="🌈 开启极光流光", variable=self.rgb_var).pack(pady=10)

        # --- 颜色选择按钮 ---
        row_btn = ttk.Frame(frame)
        row_btn.pack(fill="x", pady=5)
        ttk.Button(row_btn, text="🎨 固定颜色", command=self.pick_b).pack(side="left", expand=True, padx=2)
        ttk.Button(row_btn, text="✍ 文字颜色", command=self.pick_f).pack(side="right", expand=True, padx=2)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)

        # --- 四角文字输入 ---
        labels = {"text_tl": "左上文字", "text_tr": "右上文字", "text_bl": "左下文字", "text_br": "右下文字"}
        for key, text in labels.items():
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=text, width=12).pack(side="left")
            ent = ttk.Entry(row)
            ent.insert(0, self.app.params[key])
            ent.pack(side="right", expand=True, fill="x")
            self.entries[key] = ent

        # --- 底部确认按钮 ---
        ttk.Button(frame, text="✅ 应用并保存", command=self.apply).pack(pady=20)
        ttk.Button(frame, text="❌ 退出程序", command=self.win.destroy).pack()

    def update_speed(self, val):
        """滑动条回调：实时改变 app 中的速度参数"""
        self.app.speed = float(val)

    def pick_b(self):
        """选择边框静态颜色的调色板"""
        c = colorchooser.askcolor()[1]
        if c:
            self.app.params["color"] = c
            self.rgb_var.set(False)  # 选择固定颜色后自动关闭 RGB 模式
            self.apply()

    def pick_f(self):
        """选择文字颜色的调色板"""
        c = colorchooser.askcolor()[1]
        if c:
            self.app.params["font_color"] = c
            self.apply()

    def apply(self):
        """核心：将 UI 输入的数据同步到 app 中，并持久化到本地"""
        self.app.params["hotkey"] = self.hk_entry.get().strip().lower()
        for k, e in self.entries.items():
            self.app.params[k] = e.get()
        self.app.is_rgb = self.rgb_var.get()

        # 刷新边框绘制并保存文件
        self.app.draw_elements()
        self.app.save_config_to_file()
        messagebox.showinfo("成功", "配置已保存至本地文件！")


# 程序入口
if __name__ == "__main__":
    SettingsPanel()