import pyautogui
import os
if __name__ == '__main__':
    # 获取屏幕分辨率
    screenWidth, screenHeight = pyautogui.size()
    print(screenWidth, screenHeight)
    # 移动鼠标到屏幕中心
    pyautogui.moveTo((screenWidth / 2)+200, screenHeight / 2)
    print(os.environ['APPDATA'])