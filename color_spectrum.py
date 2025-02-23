import tkinter as tk
from tkinter import colorchooser
import colorsys
import clipboard

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
        self.num_steps_entry = tk.Entry(self.master)
        self.num_steps_entry.pack()
        self.num_steps_entry.insert(0, str(self.num_steps))  # 设置初始值
        self.update_button = tk.Button(self.master, text="更新色阶", command=self.update_num_steps)
        self.update_button.pack()

        # h_change slider
        self.h_change_label = tk.Label(self.master, text="色调变化:")
        self.h_change_label.pack()
        self.h_change_slider = tk.Scale(self.master, from_=0, to=0.2, orient=tk.HORIZONTAL, resolution=0.001, command=lambda x: self.update_colors())
        self.h_change_slider.pack()
        self.h_change_slider.set(0.01)
        
        # l_change slider
        self.l_change_label = tk.Label(self.master, text="亮度变化:")
        self.l_change_label.pack()
        self.l_change_slider = tk.Scale(self.master, from_=0, to=0.2, orient=tk.HORIZONTAL, resolution=0.01, command=lambda x: self.update_colors())
        self.l_change_slider.pack()
        self.l_change_slider.set(0.05)


        # s_change slider
        self.s_change_label = tk.Label(self.master, text="饱满度变化:")
        self.s_change_label.pack()
        self.s_change_slider = tk.Scale(self.master, from_=0, to=0.2, orient=tk.HORIZONTAL, resolution=0.01, command=lambda x: self.update_colors())
        self.s_change_slider.pack()
        self.s_change_slider.set(0.05)

        # 颜色预览区域 (使用 Frame 容纳颜色块)
        self.color_frame = tk.Frame(self.master)
        self.color_frame.pack(pady=10)

        # 反色预览区域
        self.color_frame_inverted = tk.Frame(self.master)
        self.color_frame_inverted.pack(pady=10)

    def choose_color(self):
        """打开颜色选择器并更新中间色"""
        color_code = colorchooser.askcolor(title="选择颜色")
        if color_code[0]:  # 检查是否选择了颜色
            self.central_color = tuple(c / 255 for c in color_code[0])  # 转换为 RGB (0-1)
            self.update_colors()

    def update_num_steps(self):
        """更新色阶数量并重新生成颜色"""
        try:
            self.num_steps = int(self.num_steps_entry.get())
        except ValueError:
            print("Invalid input. Please enter an integer.")
            return
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
        colors = self.generate_spectrum(self.central_color, self.num_steps)
        normal_colors = colors[:len(colors)//2]
        inverted_colors = colors[len(colors)//2:]

        for color in normal_colors:
            hex_color = self.rgb_to_hex(color)
            color_block = tk.Frame(self.color_frame, bg=hex_color, width=50, height=50, relief=tk.RAISED, borderwidth=1, cursor="hand2")
            color_block.pack(side=tk.LEFT, padx=2) #使用pack布局，padx添加颜色之间的间隔
            color_block.bind("<Button-1>", lambda event, color=hex_color, block=color_block: self.copy_color(color, block))
            self.color_blocks.append(color_block)

        for color in inverted_colors:
            hex_color = self.rgb_to_hex(color)
            color_block = tk.Frame(self.color_frame_inverted, bg=hex_color, width=50, height=50, relief=tk.RAISED, borderwidth=1, cursor="hand2")
            color_block.pack(side=tk.LEFT, padx=2) #使用pack布局，padx添加颜色之间的间隔
            color_block.bind("<Button-1>", lambda event, color=hex_color, block=color_block: self.copy_color(color, block))
            self.color_blocks.append(color_block)

    def copy_color(self, color, block):
        """将颜色复制到剪贴板"""
        clipboard.copy(color)
        block.config(borderwidth=3)
        block.after(100, lambda: block.config(borderwidth=1))

    def generate_spectrum(self, central_color, num_steps):
        """生成颜色频谱
        
        Args:
            central_color: 中心颜色 (RGB, 0-1)
            num_steps: 色阶数量 (必须是奇数，这样才有正中间的颜色)
        
        Returns:
            颜色列表 (RGB, 0-1)
        """

        # if num_steps % 2 == 0:  # 如果num_steps是偶数，增加1，以确保中心颜色位于正中间
        #     num_steps += 1

        # 转换为 HSL
        h, l, s = colorsys.rgb_to_hls(*central_color)
        l_change = self.l_change_slider.get()  # Lightness变化量
        h_change = self.h_change_slider.get()  # Hue变化量
        s_change = self.s_change_slider.get()  # Saturation变化量

        # 调整中心颜色的Lightness和Saturation
        colors = []
        half_steps = num_steps // 2

        # 生成更暗的颜色
        for i in range(half_steps, 0, -1):
            lightness = max(0, l - (l_change * i))  # Lightness减小
            saturation = max(0, s - (s_change * i))  # Saturation减小
            hue = (h - (h_change * i)) % 1  # Hue减小
            # print(hue,lightness,saturation)
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            colors.append((r, g, b))

        # 添加中心颜色
        colors.append(central_color)

        # 生成更亮的颜色
        for i in range(1, half_steps + 1):
            lightness = min(l +  (l_change * i), 1 )  # Lightness增大
            saturation = min(s + (s_change * i), 1)  # Saturation增大
            hue = (h + (h_change * i)) % 1  # Hue增大
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            colors.append((r, g, b))

        # 生成反色
        inverted_colors = []
        inverted_hue = (h + 0.5) % 1  # 反色的 Hue
        for r, g, b in colors:
            h, l, s = colorsys.rgb_to_hls(r,g,b)
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