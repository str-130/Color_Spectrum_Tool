import tkinter as tk
from tkinter import colorchooser
import colorsys

class ColorSpectrumGenerator:
    def __init__(self, master):
        self.master = master
        master.title("颜色频谱生成器")

        self.central_color = (1, 0, 0)  # 初始中间色 (RGB)
        self.num_steps = 8  # 初始色阶数量
        self.color_blocks = []  # 存储颜色块的列表

        # 创建 GUI 元素
        self.create_widgets()
        self.update_colors()  # 初始颜色生成

    def create_widgets(self):
        # 中间色选择器
        self.color_button = tk.Button(self.master, text="选择中间色", command=self.choose_color)
        self.color_button.pack(pady=10)

        # 色阶数量滑块
        self.scale_label = tk.Label(self.master, text="色阶数量:")
        self.scale_label.pack()
        self.num_steps_scale = tk.Scale(self.master, from_=3, to=20, orient=tk.HORIZONTAL,
                                          command=self.update_num_steps, label="调整色阶")
        self.num_steps_scale.set(self.num_steps)  # 设置初始值
        self.num_steps_scale.pack()

        # 颜色预览区域 (使用 Frame 容纳颜色块)
        self.color_frame = tk.Frame(self.master)
        self.color_frame.pack(pady=10)

    def choose_color(self):
        """打开颜色选择器并更新中间色"""
        color_code = colorchooser.askcolor(title="选择颜色")
        if color_code[0]:  # 检查是否选择了颜色
            self.central_color = tuple(c / 255 for c in color_code[0])  # 转换为 RGB (0-1)
            self.update_colors()

    def update_num_steps(self, value):
        """更新色阶数量并重新生成颜色"""
        self.num_steps = int(value)
        self.update_colors()

    def update_colors(self):
        """生成并更新颜色频谱"""

        # 清空之前的颜色块
        for block in self.color_blocks:
            block.destroy()  # 销毁 tkinter 窗口元素
        self.color_blocks = []  # 清空列表

        # 生成颜色
        colors = self.generate_spectrum(self.central_color, self.num_steps)

        # 创建新的颜色块
        for color in colors:
            hex_color = self.rgb_to_hex(color)
            color_block = tk.Frame(self.color_frame, bg=hex_color, width=50, height=50, relief=tk.RAISED, borderwidth=1)
            color_block.pack(side=tk.LEFT, padx=2) #使用pack布局，padx添加颜色之间的间隔
            self.color_blocks.append(color_block)

    def generate_spectrum(self, central_color, num_steps):
        """生成颜色频谱
        
        Args:
            central_color: 中心颜色 (RGB, 0-1)
            num_steps: 色阶数量 (必须是奇数，这样才有正中间的颜色)
        
        Returns:
            颜色列表 (RGB, 0-1)
        """

        if num_steps % 2 == 0:  # 如果num_steps是偶数，增加1，以确保中心颜色位于正中间
            num_steps += 1

        # 转换为 HSL
        h, s, l = colorsys.rgb_to_hls(*central_color)

        colors = []
        half_steps = num_steps // 2

        # 生成更暗的颜色
        for i in range(half_steps, 0, -1):
            lightness = max(0, l - (l / (half_steps + 1)) * i)  # Lightness减小
            r, g, b = colorsys.hls_to_rgb(h, lightness, s)
            colors.append((r, g, b))

        # 添加中心颜色
        colors.append(central_color)

        # 生成更亮的颜色
        for i in range(1, half_steps + 1):
            lightness = min(1, l + ((1 - l) / (half_steps + 1)) * i)  # Lightness增加
            r, g, b = colorsys.hls_to_rgb(h, lightness, s)
            colors.append((r, g, b))

        # 生成反色
        inverted_colors = []
        inverted_hue = (h + 0.5) % 1  # 反色的 Hue
        for r, g, b in colors:
            h, s, l = colorsys.rgb_to_hls(r,g,b)
            r, g, b = colorsys.hls_to_rgb(inverted_hue, l, s)
            inverted_colors.append((r, g, b))

        return colors + inverted_colors

    def rgb_to_hex(self, rgb):
        """将 RGB 颜色转换为十六进制颜色代码"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

# 创建主窗口并运行
root = tk.Tk()
generator = ColorSpectrumGenerator(root)
root.mainloop()