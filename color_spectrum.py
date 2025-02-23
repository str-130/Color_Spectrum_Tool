import tkinter as tk
import colorsys
import clipboard
import tkcolorpicker as tkcp
import os
import sys

# def get_resource_path(relative_path):
#     # 获取资源文件的绝对路径
#     if hasattr(sys, '_MEIPASS'):
#         # PyInstaller 打包后的路径
#         base_path = sys._MEIPASS
#         return os.path.join(base_path, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)

# image_path = get_resource_path("./frost.png")  # 假设 image1.png 在 "images" 目录下

# def verify_resource():
#     try:
#         image_path = get_resource_path('./frost.png')
#         print(f"Resource path: {image_path}")
#         print(f"Resource exists: {os.path.exists(image_path)}")
#         return True
#     except Exception as e:
#         print(f"Error accessing resource: {e}")
#         return False
    
class ColorSpectrumGenerator:
    """
    颜色频谱生成器类，用于创建一个GUI界面，允许用户选择一个中心颜色，
    然后生成一个基于该中心颜色的颜色频谱。用户可以通过调整色阶数量、
    色调变化、亮度变化和饱和度变化来定制颜色频谱。
    """
    def __init__(self, master):
        """
        初始化颜色频谱生成器。

        Args:
            master: Tkinter 的主窗口。
        """
        self.master = master
        master.title("颜色频谱生成器")
        # 设置窗口的最小大小
        master.minsize(800, 400)

        # 为行和列设置权重，使其居中
        master.grid_rowconfigure(0, weight=1)        # 顶部空白
        master.grid_columnconfigure(0, weight=1)     # 左侧空白
        master.grid_rowconfigure(8, weight=1)        # 底部空白 (假设总共有 7 行内容)
        master.grid_columnconfigure(0, weight=1)     # 右侧空白 （假设总共有 3 列内容）

        # 设置列的最小宽度和权重（内容列）
        master.grid_columnconfigure(0, minsize=100, weight=0) # 标签列
        master.grid_columnconfigure(1, minsize=200, weight=0) # 主体内容列 (输入框/滑块)        
        master.grid_columnconfigure(2, minsize=200, weight=0) # 主体内容列 (输入框/滑块)    
        master.grid_columnconfigure(3, minsize=300, weight=0) # 主体内容列 (输入框/滑块)    

        default_color = (240,138,93)

        self.central_color = tuple(c / 255.0 for c in default_color)  # 初始中间色 (RGB)
        self.num_steps = 8  # 初始色阶数量
        self.color_blocks = []  # 存储颜色块的列表

        # 创建 GUI 元素
        self.create_widgets()
        self.update_colors()  # 初始颜色生成

    def create_widgets(self):
        """创建 GUI 元素"""

        # 第二行：色阶数量
        self.scale_label = tk.Label(self.master, text="色阶数量:")
        self.scale_label.grid(row=2, column=1, sticky="w")
        self.num_steps_slider = tk.Scale(
            self.master, from_=4, to=16, orient=tk.HORIZONTAL, resolution=2,
            command=lambda x: self.update_num_steps(), length=150
        )
        self.num_steps_slider.grid(row=2, column=2, columnspan=1, pady=5, sticky="w")
        self.num_steps = 8  # 设置初始值
        self.num_steps_slider.set(8)

        # 第一行：颜色选择器
        self.color_button = tk.Button(self.master, text="选择中间色", command=self.choose_color)
        self.color_button.grid(row=2, column=3, columnspan=1, pady=10,sticky="w")

        # 添加当前色块
        self.current_color_block = tk.Frame(
            self.master, 
            width=50, 
            height=50, 
            relief=tk.RAISED, 
            borderwidth=1
        )
        self.current_color_block.grid(row=2, column=3, pady=10, padx=(100, 0), sticky="w")
        # 确保Frame保持指定大小
        self.current_color_block.pack_propagate(False)

        # 设置初始颜色
        initial_color = self.rgb_to_hex(self.central_color)
        self.current_color_block.configure(bg=initial_color)
        
        # 第三行：色调, 亮度, 饱和度调整
        self.h_change_label = tk.Label(self.master, text="色调变化:")
        self.h_change_label.grid(row=3, column=1, sticky="w")
        self.h_change_slider = tk.Scale(
            self.master, from_=-30, to=30, orient=tk.HORIZONTAL, resolution=1,
            command=lambda x: self.update_colors(), length=300
        )
        self.h_change_slider.grid(row=3, column=2, columnspan=2, sticky="w")
        self.h_change_slider.set(2)

        self.l_change_label = tk.Label(self.master, text="亮度变化:")
        self.l_change_label.grid(row=4, column=1, sticky="w")
        self.l_change_slider = tk.Scale(
            self.master, from_=0, to=20, orient=tk.HORIZONTAL, resolution=1,
            command=lambda x: self.update_colors(), length=300
        )
        self.l_change_slider.grid(row=4, column=2, columnspan=2, sticky="w")
        self.l_change_slider.set(5)

        self.s_change_label = tk.Label(self.master, text="饱满度变化:")
        self.s_change_label.grid(row=5, column=1, sticky="w")
        self.s_change_slider = tk.Scale(
            self.master, from_=-5, to=20, orient=tk.HORIZONTAL, resolution=1,
            command=lambda x: self.update_colors(), length=300
        )
        self.s_change_slider.grid(row=5, column=2, columnspan=2, sticky="w")
        self.s_change_slider.set(5)

        # 第四行：颜色预览
        self.color_frame = tk.Frame(self.master)
        self.color_frame.grid(row=6, column=0, columnspan=4, pady=10)

        # 第五行：反色预览区域
        self.color_frame_inverted = tk.Frame(self.master)
        self.color_frame_inverted.grid(row=7, column=0, columnspan=4, pady=10)



    def choose_color(self):
        """
        打开颜色选择器并更新中间色。
        """
        initial_color = self.rgb_to_hex(self.central_color)
        color_code = tkcp.askcolor(title="选择颜色", color=initial_color)
        if color_code[1]:  # 检查是否选择了颜色
            hex_color = str(color_code[1])
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            self.central_color = (r / 255, g / 255, b / 255)  # 转换为 RGB (0-1)
            # 更新当前色块
            self.current_color_block.configure(bg=hex_color)
            self.update_colors()

    def update_num_steps(self):
        """
        更新色阶数量并重新生成颜色。
        """
        self.num_steps = int(self.num_steps_slider.get())
        self.update_colors()

    def update_colors(self):
        """
        生成并更新颜色频谱。
        """

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
            color_block = tk.Frame(self.color_frame, bg=hex_color, width=40, height=40, relief=tk.RAISED, borderwidth=1, cursor="hand2")
            color_block.pack(side=tk.LEFT, padx=2) #使用pack布局，padx添加颜色之间的间隔
            color_block.bind("<Button-1>", lambda event, color=hex_color, block=color_block: self.copy_color(color, block))
            self.color_blocks.append(color_block)

        for color in inverted_colors:
            hex_color = self.rgb_to_hex(color)
            color_block = tk.Frame(self.color_frame_inverted, bg=hex_color, width=40, height=40, relief=tk.RAISED, borderwidth=1, cursor="hand2")
            color_block.pack(side=tk.LEFT, padx=2) #使用pack布局，padx添加颜色之间的间隔
            color_block.bind("<Button-1>", lambda event, color=hex_color, block=color_block: self.copy_color(color, block))
            self.color_blocks.append(color_block)

    def copy_color(self, color, block):
        """
        将颜色复制到剪贴板。

        Args:
            color: 要复制的颜色 (十六进制代码)。
            block: 颜色块 (Tkinter Frame)。
        """
        clipboard.copy(color)
        block.config(borderwidth=3)
        block.after(100, lambda: block.config(borderwidth=1))

    def generate_spectrum(self, central_color, num_steps):
        """
        生成颜色频谱。
        
        Args:
            central_color: 中心颜色 (RGB, 0-1)。
            num_steps: 色阶数量 (必须是奇数，这样才有正中间的颜色)。
        
        Returns:
            颜色列表 (RGB, 0-1)。
        """

        # if num_steps % 2 == 0:  # 如果num_steps是偶数，增加1，以确保中心颜色位于正中间
        #     num_steps += 1

        # 转换为 HSL
        h, l, s = colorsys.rgb_to_hls(*central_color)
        l_change = self.l_change_slider.get() / 100  # Lightness变化量
        h_change = self.h_change_slider.get() / 360 # Hue变化量
        s_change = self.s_change_slider.get() / 100 # Saturation变化量

        # 调整中心颜色的Lightness和Saturation
        colors = []
        half_steps = num_steps // 2

        # 生成更暗的颜色
        for i in range(half_steps, 0, -1):
            lightness = max(0, l - (l_change * i))  # Lightness减小
            saturation = min( s - (s_change * i),1)  # Saturation减小
            hue = (h - (h_change * i)) % 1  # Hue减小
            # print(hue,lightness,saturation)
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            colors.append((r, g, b))

        # 添加中心颜色
        colors.append(central_color)

        # 生成更亮的颜色
        for i in range(1, half_steps + 1):
            lightness = min(l +  (l_change * i), 1 )  # Lightness增大
            saturation = min(s - (s_change * i), 1)  # Saturation增大
            hue = (h + (h_change * i)) % 1  # Hue增大
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            colors.append((r, g, b))

        # 生成反色
        inverted_colors = []
        for r, g, b in colors:
            h, l, s = colorsys.rgb_to_hls(r,g,b)
            inverted_hue = (h + 0.5) % 1  # 反色的 Hue
            r, g, b = colorsys.hls_to_rgb(inverted_hue, l, s)
            inverted_colors.append((r, g, b))

        return colors + inverted_colors

    def rgb_to_hex(self, rgb):
        """
        将 RGB 颜色转换为十六进制颜色代码。

        Args:
            rgb: RGB 颜色 (tuple of floats, 0-1)。

        Returns:
            十六进制颜色代码 (string)。
        """
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

# 创建主窗口并运行
root = tk.Tk()
root.geometry("800x400")
root.resizable(False, False)
# verify_resource()
# image_path = get_resource_path("frost.png")
# root.iconphoto(False, tk.PhotoImage(file="./frost.png"))
generator = ColorSpectrumGenerator(root)
root.mainloop()
