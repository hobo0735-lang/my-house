import tkinter as tk
import keyboard  # 请确保已执行 pip install keyboard
import threading
import time


class StableBorder:
    def __init__(self):
        self.root = None
        self.active = False
        self.last_press_time = 0
        self.border_width = 100  # 足够大的显示器边框
        self.border_color = "lime"  # 显眼的亮绿色

    def setup_ui(self):
        """初始化时就把窗口准备好，并设为隐藏"""
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-transparentcolor", "white", "-alpha", 0.7)

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")

        canvas = tk.Canvas(self.root, bg="white", highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        # 预先画好大边框
        w = self.border_width
        canvas.create_rectangle(w / 2, w / 2, sw - w / 2, sh - w / 2, outline=self.border_color, width=w)

        # 初始状态：隐藏
        self.root.withdraw()
        self.root.mainloop()

    def toggle(self):
        """核心：通过切换显示状态来规避卡死"""
        current_time = time.time()
        # 防抖处理：0.3秒内连续按键无效
        if current_time - self.last_press_time < 0.3:
            return
        self.last_press_time = current_time

        if self.root:
            if not self.active:
                self.root.deiconify()  # 瞬间显现
            else:
                self.root.withdraw()  # 瞬间隐藏
            self.active = not self.active


app = StableBorder()

# 在守护线程中启动 UI，确保主程序退出时它也退出
threading.Thread(target=app.setup_ui, daemon=True).start()


def on_f9():
    app.toggle()


# 使用底层监听，并绑定触发函数
keyboard.add_hotkey('f9', on_f9)

print(">>> 稳健版启动成功！")
print(">>> 已采用‘预加载’技术，连续狂按 F9 也不会卡死。")

keyboard.wait()