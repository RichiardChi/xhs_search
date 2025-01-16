import rpa as r
import time
import traceback
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.common_utils import scroll_down
from utils.xhs_note_parse import parse_xhs_note

if __name__ == '__main__':
    # with open(r'D:\xhs_rpa_prompt.txt', 'r', encoding='utf-8') as file:
    #     prompt = file.readlines()
    # with open(r'D:\xhs_rpa_config.txt', 'r', encoding='utf-8') as file:
    #     config_json = json.load(file)
    #     print('配置文件：', config_json)
    try:
        # 初始化 WebDriver
        driver = webdriver.Chrome()
        # 打开小红书网站
        driver.get('https://www.xiaohongshu.com/explore')
        time.sleep(3000)
        # 最大化窗口
        pyautogui.hotkey('win', 'up')
        # r.keyboard("[win][up]")
        # r.keyboard("[alt][space]")
        # r.keyboard("x")
        # 创建一个等待对象，等待时间不超过10秒
        wait = WebDriverWait(driver, 10)
        for index, loop_search_keyword in enumerate(config_json['search_keywords']):
            print(index, loop_search_keyword)
            # 点击搜索
            # 使用 XPath 定位按钮
            button_xpath = '//*[@id=\"search-input\"]'  # 替换为实际的 XPath
            button_element = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            # 点击按钮
            button_element.click()

            # 使用 XPath 定位输入框
            input_xpath = '//*[@id=\"search-input\"]'  # 替换为实际的 XPath
            input_element = wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
            # 输入文本
            input_element.send_keys(loop_search_keyword)
            # pyautogui.typewrite(loop_search_keyword)
            time.sleep(3000)
            r.click('/html/body/div[2]/div[1]/div[1]/header/div[2]/div')
            time.sleep(3000)
            # 循环点击前5条
            for num in range(1, 3):
                # 依次打开文章详情
                r.click("//*[@id=\"global\"]/div[2]/div[2]/div/div[3]/section[%s]/div/a[2]" % num)
                time.sleep(3000)
                # 点击文章标题
                r.hover('/html/body/div[6]/div[1]/div[4]/div[2]/div[1]/div[1]')
                # r.hover("//*[@id='detail-title']")
                r.click("//*[@id='detail-title']")
                time.sleep(3000)
                # 获取当前鼠标位置
                currentMouseX, currentMouseY = pyautogui.position()
                print(f'鼠标位置({currentMouseX},{currentMouseY})')
                pyautogui.click(currentMouseX, currentMouseY - 50)
                scroll_down(-800, 15)
                time.sleep(3000)
                # 读取网页html
                detail_html = r.read('page')
                # print('读取网页：',detail_html)
                html_parse_result = parse_xhs_note(detail_html)
                print(html_parse_result)
                # TODO 调用llm
                # 点击复制链接
                r.click("//*[@id=\"noteContainer\"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[2]")
                time.sleep(3000)
                # 从剪切板获取文本
                share_link = pyperclip.paste()
                print('获取链接', share_link)
                # 返回到查询页面
                pyautogui.hotkey('esc')
            if index == 1:
                break
    except Exception as e:
        traceback.print_exc()

