import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import sounddevice as sd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import textwrap
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class AnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("语音纠错")
        self.root.configure(bg='lightblue')  # 设置窗口背景颜色为浅蓝色

        self.button = tk.Button(root,
                                text="开始录音",
                                command=self.start_waveform,
                                width=20,
                                height=2)
        self.button.pack(pady=20)

        self.figure = plt.Figure(figsize=(5, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

        self.stream = None
        self.ani = None
        self.ax.axis('off')

        self.state = "idle"  # 初始状态

        # 动画相关变量
        self.frames = []
        self.current_frame = 0
        self.image_on_canvas = None

        # 文本显示相关变量
        self.text_obj = None
        self.current_char_index = 0
        self.dream_text = ""
        self.text_lines = []

        # 设置支持中文的字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

    def start_waveform(self):
        if self.state == "idle":
            self.button.config(text="结束录音")
            self.state = "running"

            sample_rate = 44100  # 44.1 kHz
            buffer_size = 1024  # 每次读取的样本数
            window_size = 4096  # 滑动窗口大小
            step_size = 128  # 每次更新时滚动的样本数

            self.stream = sd.InputStream(samplerate=sample_rate, channels=1, blocksize=buffer_size)
            self.stream.start()

            self.ax.set_xlim(0, window_size)
            self.ax.axis('off')
            self.ax.set_ylim(-1, 1)

            self.line, = self.ax.plot([], [], lw=2)
            self.audio_buffer = np.zeros(window_size)

            self.ani = animation.FuncAnimation(
                self.figure, self.update, frames=200, init_func=self.init, blit=True, interval=20
            )
        elif self.state == "running":
            self.button.config(text="分析纠错")
            self.state = "stopped"

            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.ani.event_source.stop()
            self.ani = None

            # 清除波形图像
            self.ax.clear()
            self.ax.axis('off')
            self.canvas.draw()

        elif self.state == "stopped":
            self.display_dream_text()
            self.state = "over"  # 将状态设置为 over

        elif self.state == "over":
            # 在 over 状态下，按钮不会有任何响应
            pass

    def display_dream_text(self):
        dream_text = "袁隆平一直有一个梦想，“我做了一个梦，梦见我那个水稻长得比高粱还高，穗子比扫(4->1)帚还长。太阳晒起来，我跟我的同事就坐在那个稻(4->3)穗下乘凉 … …”"
        print(len(dream_text))
        color_list = [1] * len(dream_text)
        color_list[37] = 2# 示例颜色列表
        color_list[38:45] = [4] * 6

        color_list[65] = 2
        color_list[66:78] = [4] * 6
        self.dream_text = dream_text
        self.current_char_index = 0
        self.text_lines = textwrap.wrap(dream_text, width=25)  # 指定每行的最大字符数
        self.color_list = color_list  # 添加颜色列表
        self.update_text_label()

    def update_text_label(self):
        if self.current_char_index < len(self.dream_text):
            current_char = self.dream_text[self.current_char_index]

            # 定义颜色映射
            color_map = {
                1: 'black',
                2: 'red',
                3: 'blue',
                4: 'green'
            }

            # 计算文本的宽度和高度
            num_chars = len(self.dream_text[:self.current_char_index + 1])
            num_lines = len(self.text_lines)
            chars_per_line = len(self.text_lines[0]) if self.text_lines else 0

            # 计算当前字符的位置
            line_index = self.current_char_index // chars_per_line
            char_index_in_line = self.current_char_index % chars_per_line

            x_offset = 0.5 - chars_per_line * 0.02 + char_index_in_line * 0.04  # 调整 x 偏移以居中显示
            y_offset = 0.8 - line_index * 0.1  # 调整 y 偏移以居中显示

            color_index = self.color_list[self.current_char_index]
            color = color_map.get(color_index, 'black')  # 默认颜色为黑色

            # 创建并添加新的字符对象
            text_obj = self.ax.text(x_offset, y_offset, current_char, ha='center', va='center', fontsize=12,
                                    fontproperties=FontProperties(family='SimHei'), color=color)
            self.ax.add_artist(text_obj)

            self.current_char_index += 1
            #print(f"Updated text: {current_char}")  # 调试信息
            self.canvas.draw_idle()  # 确保画布重新绘制
            self.root.after(100, self.update_text_label)  # 每100毫秒更新一次

    def init(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        sample_rate = 44100  # 44.1 kHz
        buffer_size = 1024  # 每次读取的样本数
        window_size = 4096  # 滑动窗口大小
        step_size = 128  # 每次更新时滚动的样本数
        data, overflowed = self.stream.read(buffer_size)
        new_data = data[:, 0]  # 取单声道数据

        self.audio_buffer = np.roll(self.audio_buffer, -step_size)
        self.audio_buffer[-step_size:] = new_data[:step_size]

        self.line.set_data(np.arange(window_size), self.audio_buffer)
        return self.line,

    def update_frame(self):
        if self.current_frame < len(self.frames):
            frame = self.frames[self.current_frame]
            # 将 PIL.Image 对象转换为 NumPy 数组
            frame_np = np.array(frame)
            self.ax.imshow(frame_np, aspect='auto')
            self.ax.axis('off')
            self.ax.figure.canvas.draw()
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.root.after(100, self.update_frame)  # 每100毫秒更新一次

    def play_animation(self):
        self.update_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationApp(root)
    root.mainloop()
