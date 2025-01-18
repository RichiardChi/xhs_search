import os

import json
import traceback
import pyautogui
import pyperclip

from DrissionPage import ChromiumPage

from utils import json_formatter, wechat_utils
from utils.clue_analyze import ask_llm
from utils.common_utils import scroll_down, activate_window
from utils.xhs_note_parse import parse_xhs_note
work_dir = os.getcwd()
if __name__ == '__main__':
    with open(os.path.join(os.getcwd(),'xhs_rpa_config.txt'),'r',encoding='utf-8') as file:
        config_json = json.load(file)
        print('配置文件：',config_json)
    try:
        # 创建对象
        page = ChromiumPage()
        #打开小红书网站
        page.get('https://www.xiaohongshu.com/explore')
        page.wait(3)
        # 激活浏览器窗口
        activate_window('.*小红书.*')
        page.wait(3)
        # 最大化窗口
        pyautogui.hotkey('alt', 'space')
        pyautogui.hotkey('x')
        pyautogui.hotkey('esc')
        for index,loop_search_keyword in enumerate(config_json['search_keywords']):
            print(index,loop_search_keyword)
            page('xpath:/html/body/div[2]/div[1]/div[1]/header/div[2]/input').click()
            # 删除原搜索框内容
            if page.ele('xpath:/html/body/div[2]/div[1]/div[1]/header/div[2]/input').value !='' :
                page('xpath:/html/body/div[2]/div[1]/div[1]/header/div[2]/div/div[1]').click()
            # 点击搜索框
            try:
                page.wait(3)
                page('xpath://*[@id=\"search-input\"]').input(loop_search_keyword)
                # pyautogui.typewrite(loop_search_keyword)
            except Exception as e:
                # traceback.print_exc()
                pass
            page.wait(3)
            # 点击搜索
            page('xpath:/html/body/div[2]/div[1]/div[1]/header/div[2]/div/div[2]').click()
            page.wait(5)
            # 循环点击前2条
            for num in range(1,3):
                page.wait(1)
                #依次打开文章详情/html/body/div[2]/div[1]/div[2]/div[2]/div/div[3]/section[2]/div
                page("xpath:/html/body/div[2]/div[1]/div[2]/div[2]/div/div[3]/section[%s]/div"%num).click()
                page.wait(3)

                # 获取屏幕分辨率
                screenWidth, screenHeight = pyautogui.size()
                print(screenWidth, screenHeight)
                # 移动鼠标到屏幕中心
                pyautogui.moveTo((screenWidth / 2) + screenWidth/10, screenHeight / 2)
                # 鼠标向下滑动
                scroll_down(-800,15)
                page.wait(2)
                # 点击复制链接
                page("xpath://*[@id=\"noteContainer\"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[2]").click()
                page.wait(2)
                # 从剪切板获取文本
                share_link = pyperclip.paste()
                print('文章链接：', share_link)
                # 读取网页html
                detail_html = page.html
                # print('读取网页：',detail_html)
                html_parse_result = parse_xhs_note(detail_html)
                print(html_parse_result)
                #TODO 调用llm
                ai_result_json = ask_llm(html_parse_result)
                if len(ai_result_json)>0:
                    title = "文章标题：" + ai_result_json[0]['note_title'] + "\n"
                    print('文章标题：',title)
                    clue_desc_str = json_formatter.format_clue_list_to_str(ai_result_json)
                    print('大模型返回结果：', clue_desc_str)
                    message =  f'{share_link}\n  ------------------------\n{clue_desc_str}'
                    print('微信消息：',message)
                    # 发送微信消息
                    for user in config_json['at_user_list']:
                        wechat_utils.send_wechat_msg(user, [message])
                # 激活浏览器窗口
                activate_window('.*小红书.*')
                # 返回到查询页面
                page("xpath://div[@class='close close-mask-dark']").click()
                page.wait(1)
            # 测试搜索两个关键词
            if index == 1 :
                break
    except Exception as e:
        traceback.print_exc()


