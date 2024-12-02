import os
import tkinter as tk
from PIL import Image, ImageTk

def load_frames(directory):
    frames = []
    for filename in sorted(os.listdir(directory)):
        if filename.startswith('frame_') and filename.endswith('.png'):
            frame_path = os.path.join(directory, filename)
            frame = Image.open(frame_path)
            frames.append(frame)
    return frames

def update_frame(index):
    global current_frame
    if index < len(frames):
        frame = frames[index]
        photo = ImageTk.PhotoImage(frame)
        canvas.itemconfig(image_on_canvas, image=photo)
        canvas.image = photo  # 避免垃圾回收
        current_frame = (current_frame + 1) % len(frames)
        root.after(100, update_frame, current_frame)  # 每100毫秒更新一次

def main():
    global root, canvas, image_on_canvas, frames, current_frame

    # 初始化Tkinter
    root = tk.Tk()
    root.title('Animation')

    # 加载所有帧
    frames = load_frames('frames')
    if not frames:
        print("没有找到任何帧文件")
        return

    # 创建Canvas
    canvas = tk.Canvas(root, width=frames[0].width, height=frames[0].height)
    canvas.pack()

    # 显示第一帧
    photo = ImageTk.PhotoImage(frames[0])
    image_on_canvas = canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo  # 避免垃圾回收

    # 开始动画
    current_frame = 0
    update_frame(current_frame)

    # 进入主循环
    root.mainloop()

if __name__ == '__main__':
    main()
