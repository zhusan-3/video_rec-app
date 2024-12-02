import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import sounddevice as sd

# 设置采样率和缓冲区大小
sample_rate = 44100  # 44.1 kHz
buffer_size = 1024  # 每次读取的样本数
window_size = 4096  # 滑动窗口大小
step_size = 128  # 每次更新时滚动的样本数

# 初始化音频流
stream = sd.InputStream(samplerate=sample_rate, channels=1, blocksize=buffer_size)
stream.start()

# 设置图形参数
fig, ax = plt.subplots()
ax.set_xlim(0, window_size)
ax.set_ylim(-1, 1)

# 初始化线条
line, = ax.plot([], [], lw=2)

# 缓冲区
audio_buffer = np.zeros(window_size)


# 初始化函数
def init():
    line.set_data([], [])
    return line,


# 更新函数
def update(frame):
    global audio_buffer
    data, overflowed = stream.read(buffer_size)
    new_data = data[:, 0]  # 取单声道数据

    # 将新数据添加到缓冲区的末尾
    audio_buffer = np.roll(audio_buffer, -step_size)
    audio_buffer[-step_size:] = new_data[:step_size]

    # 更新线条的数据
    line.set_data(np.arange(window_size), audio_buffer)
    return line,


# 创建动画
ani = animation.FuncAnimation(fig, update, frames=200, init_func=init, blit=True, interval=20)

# 显示动画
plt.show()

# 关闭音频流
stream.stop()
stream.close()
