import time

import pyautogui
import pyperclip
import uiautomation as auto

from utils.common_utils import activate_window


def send_wechat_msg(wechat_name:str='文件传输助手',messages:[]=['你好']):
    # 定位微信的主窗口
    wechat_window = auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC', SubName='微信')

    # 激活窗口
    wechat_window.SetActive()
    # # 将窗口设置为最顶层，确保它在所有其他窗口之上
    # wechat_window.SetTopmost(True)
    time.sleep(1)
    # 定位微信的搜索框并输入搜索内容
    wechat_window.ButtonControl(Name="通讯录").Click()
    search_box = wechat_window.EditControl(Name="搜索")
    search_box.Click()
    time.sleep(1)
    search_box.SendKeys(wechat_name)  # 这里输入微信id/昵称/备注
    time.sleep(1)
    # 模拟回车键来执行搜索操作
    auto.SendKey(auto.Keys.VK_RETURN)

    # 搜索结果显示在列表中
    auto.WaitForExist(wechat_window, 5)  # 等待5秒钟确保搜索结果加载完毕

    # 定位包含搜索结果的列表控件
    search_results_list = auto.ListControl(searchFromControl=wechat_window)

    # 获取搜索结果中的联系人信息
    # if search_results_list.Exists():
    #     items = search_results_list.GetChildren()
    #     if items:
    #         # 假设点击第一个搜索结果
    #         first_contact = items[0]
    #         first_contact.Click()
    #         print('==============', first_contact)
    #     else:
    #         print("未找到搜索结果.")
    # else:
    #     print("未找到搜索结果列表控件.")

    # 检查搜索结果列表是否存在
    if search_results_list.Exists():
        items = search_results_list.GetChildren()
        if items:
            # 点击第一个搜索结果
            first_contact = items[0]
            first_contact.Click()

            # 聊天窗口打开后，找到消息输入框
            input_box = wechat_window.ListControl(Name='消息')
            # if input_box.Exists():
            #     # 输入消息内容
            #     input_box.SendKeys('你好')

            #     send_button = wechat_window.ButtonControl(Name='发送(S)')

            #     if send_button.Exists():
            #         # 点击发送按钮
            #         send_button.Click()
            #     else:
            #         print("未找到发送按钮")
            # else:
            #     print("未找到消息输入框")
            if input_box.Exists():
                # messages = ['你好', '今天天气真好', '有什么好玩的推荐吗？', '我刚刚看到了一篇有趣的文章', '晚安']
                time.sleep(1)
                for message in messages:
                    # input_box.SendKeys(message)
                    # input_box.Click()
                    # 复制粘贴方式
                    pyperclip.copy(message)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(1)
                    auto.SendKeys('{ENTER}')  # 发送消息enter
            else:
                print("未找到消息输入框")
        else:
            print("未找到搜索结果.")
    else:
        print("搜索结果列表不存在.")
if __name__ == '__main__':
    title = '文章标题：无限机场贵宾厅，你都用哪张💳'
    share_link = '  【无限机场贵宾厅，你都用哪张 - 银行搬砖民工 | 小红书 - 你的生活指南】  C11dD8o7jTCt7Fs  https://www.xiaohongshu.com/discovery/item/66ee9ad80000000027005833?source=webshare&xhsshare=pc_web&xsec_token=ABQqT7yeW5tqBw-IlqgTrzJ8XqKZ3MYKyrrufi54V1c1g=&xsec_source=pc_share'
    clue_desc_str = '''
    用户名：miss淼淼🥂
    评论内容：中行招财猫金卡可以进贵宾厅吗
    评论时间：2024-12-27
    线索分析：客户对信用卡的贵宾厅服务感兴趣
    线索得分（满分100分）：90
    ------------------------
    用户名：小红薯6252B92E
    评论内容：有免年费的卡吗
    评论时间：2024-10-26
    线索分析：客户在询问免年费的信用卡
    线索得分（满分100分）：85
    ------------------------'''
    # message = title + '\n' + share_link + '\n' + clue_desc_str
    message = f'{share_link}\n    ------------------------\n{clue_desc_str}'
    pyperclip.copy(message)
    print(pyperclip.paste())
    send_wechat_msg('文件传输助手',[pyperclip.paste()])
    activate_window('.*小红书.*')