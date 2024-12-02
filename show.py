import time

def display_text_animated(text, delay=0.1):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # 换行

dream_text = "袁隆平一直有一个梦想，“我做了一个梦，梦见我那个水稻长得比 高粱还高，穗子比扫帚还长。太阳晒起来，我跟我的同事就坐在那个稻 穗下乘凉 … …”"

display_text_animated(dream_text)
