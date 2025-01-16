import pyautogui,time
from pywinauto import Application,findwindows
# 滚动函数
def scroll_down(distance, times):
    for _ in range(times):
        pyautogui.scroll(distance)
        time.sleep(0.5)  # 暂停0.5秒，防止过度滚动

def activate_window(window_title):
    # 连接到已经打开的记事本应用程序
    app = Application(backend='win32').connect(title_re=window_title)
    # 获取窗口
    window = app.window(title_re=window_title)
    # 激活窗口
    window.set_focus()

if __name__ == '__main__':
    # 列出所有窗口的标题
    windows = findwindows.find_elements()
    # for window in windows:
    #     print(window.name)
    activate_window('.*小红书.*')
