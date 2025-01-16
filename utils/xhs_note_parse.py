# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import json, logging, time, re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib


def is_followed_user(username: str):
    """
    从mongodb中查询是否已跟进用户
    Returns:
        bool: 是否已跟进用户
    """
    conn = get_mongodb_connection(db_name="xhs_note", collection_name="followed_users")
    if conn is not None:
        return conn.find_one({"_id": hashlib.md5(username.encode('utf-8')).hexdigest()}) is not None
    else:
        return False


def get_mongodb_connection(db_name: str = "xhs_note", collection_name: str = "followed_notes"):
    """
    获取MongoDB连接
    Args:
        db_name (str): 数据库名称,默认xhs_note
        collection_name (str): 集合名称,默认followed_notes
    Returns:
        collection: 集合对象
    """
    try:
        client = MongoClient(
            'mongodb://root:sk=6708eadAA*!@dds-bp160a8a0c7394841413-pub.mongodb.rds.aliyuncs.com:3717/')
        db = client[db_name]  # 数据库名称
        collection = db[collection_name]  # 集合名称
        return collection
    except Exception as e:
        print(f"MongoDB连接失败: {str(e)}")
        print(f"MongoDB连接失败: {str(e)}")
        return None


def parse_xhs_note(html_content, note_url: str = "") -> str:
    try:
        print("开始解析HTML内容")
        start_time = time.time()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取标题
        title_elem = soup.find('div', id='detail-title')
        if not title_elem:
            print("未找到标题元素")
            title = ""
        else:
            title = title_elem.get_text(strip=True)

        # 提取正文
        content_elem = soup.find('div', id='detail-desc')
        if not content_elem:
            print("未找到正文元素")
            content = ""
        else:
            content = content_elem.find('span', class_='note-text')
            content = content.get_text(strip=True) if content else ""

        # 提取评论列表
        comments = soup.find('div', class_='comments-container')
        comment_list = []

        if comments:
            for comment_div in comments.find_all('div', class_='comment-item'):
                try:
                    comment = {}

                    # 提取评论用户名
                    username_elem = comment_div.find('a', class_='name')
                    username = username_elem.get_text(strip=True) if username_elem else ""

                    # 如果用户在已跟进列表中，跳过该评论
                    # comment['need_to_follow'] = 0 if is_followed_user(username) else 1

                    comment['nick_name'] = username

                    # 提取评论日期并进行时间判断
                    date_elem = comment_div.find('div', class_='date')
                    if date_elem:
                        date_span = date_elem.find('span')
                        comment_date = date_span.get_text(strip=True) if date_span else ""
                        # 提取城市信息
                        location_span = date_elem.find('span', class_='location')
                        comment['location'] = location_span.get_text(strip=True) if location_span else ""
                        # 如果评论时间超过7天，则标记为不需要跟进
                        comment['need_to_follow'] = 0 if not is_within_days(comment_date) or comment[
                            'need_to_follow'] == 0 else 1
                        comment['comment_time'] = comment_date
                    else:
                        comment['comment_time'] = ""

                    # 提取评论内容
                    content_elem = comment_div.find('span', class_='note-text')
                    if content_elem:
                        comment['comment_content'] = content_elem.get_text(strip=True)

                    # 提取评论回复按钮的CSS选择器
                    css_selector = generate_css_selector(comment_div)
                    if css_selector:
                        comment['reply_button_selector'] = css_selector

                    # 处理回复列表
                    replies = comment_div.find('div', class_='reply-container')
                    reply_list = []

                    if replies:
                        for reply_div in replies.find_all('div', class_='comment-item'):
                            try:
                                # 提取回复用户名
                                reply_username = reply_div.find('a', class_='name')
                                username = reply_username.get_text(strip=True) if reply_username else ""

                                reply = {}

                                # reply['need_to_follow'] = 0 if is_followed_user(username) or reply[
                                #     'need_to_follow'] == 0 else 1

                                # 提取评论日期并进行时间判断
                                reply_date_elem = reply_div.find('div', class_='date')
                                if reply_date_elem:
                                    reply_date_span = reply_date_elem.find('span')
                                    reply_date = reply_date_span.get_text(strip=True) if date_span else ""
                                    # 如果评论时间超过7天，则标记为不需要跟进
                                    reply['need_to_follow'] = 0 if not is_within_days(reply_date) or reply[
                                        'need_to_follow'] == 0 else 1
                                    reply['comment_time'] = reply_date
                                else:
                                    reply['comment_time'] = ""
                                # 提取城市信息
                                location_span = reply_date_elem.find('span', class_='location')
                                reply['location'] = location_span.get_text(strip=True) if location_span else ""

                                reply['nick_name'] = username
                                # 提取回复内容
                                reply_content = reply_div.find('span', class_='note-text')
                                if reply_content:
                                    reply['comment_content'] = reply_content.get_text(strip=True)

                                # 提取回复的回复按钮CSS选择器
                                css_selector = generate_css_selector(reply_div)
                                if css_selector:
                                    reply['reply_button_selector'] = css_selector

                                reply_list.append(reply)
                            except Exception as e:
                                print(f"解析回复出错: {str(e)}")
                                continue

                    comment['comment_list'] = reply_list
                    comment_list.append(comment)

                except Exception as e:
                    print(f"解析评论出错: {str(e)}")
                    continue

        # 提取作者信息
        author_elem = soup.find('div', class_='author-wrapper').find('span', class_='username')
        author = author_elem.get_text(strip=True) if author_elem else ""

        # 生成标题和作者的组合字符串
        unique_str = f"{title}_{author}".encode('utf-8')
        # 计算MD5值作为_id
        id = hashlib.md5(unique_str).hexdigest()

        result = {
            "_id": id,
            "note_title": title,
            "note_url": note_url,
            "note_author": author,
            "note_content": content,
            "comment_list": comment_list,
            "follow_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # store_note_to_mongodb(result)

        end_time = time.time()
        print(f"解析完成,耗时: {end_time - start_time:.2f}秒")

        # 对result里面的评论做一个过滤，如果need_to_follow为1或者子评论列表中存在need_to_follow为1的，则保留，否则删除
        # note = filter_comment(result)
        return json.dumps(result, ensure_ascii=False, indent=4)
        # return json.dumps(note, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"解析整体出错: {str(e)}")
        return f"解析出错: {str(e)}"


def filter_comment(note):
    """
    过滤评论，如果need_to_follow为1或者子评论列表中存在need_to_follow为1的，则保留，否则删除
    使用列表推导式和递归来优化性能
    """
    # 先递归处理所有子评论
    for comment in note['comment_list']:
        filter_comment(comment)

    # 使用列表推导式过滤评论
    note['comment_list'] = [
        comment for comment in note['comment_list']
        if comment['need_to_follow'] == 1 or
           any(reply['need_to_follow'] == 1 for reply in comment['comment_list'])
    ]

    return note


def store_note_to_mongodb(note):
    """
    将解析结果存储到MongoDB
    """
    try:
        collection = get_mongodb_connection(db_name="xhs_note", collection_name="followed_notes")
        if collection is not None:
            # 使用_id进行更新，不再需要单独的unique_id字段
            collection.replace_one(
                {"_id": note['_id']},
                note,
                upsert=True
            )
            print(f"笔记数据已成功存储到MongoDB，_id: {note['_id']}")
            print(f"笔记数据已成功存储到MongoDB，_id: {note['_id']}")

    except Exception as e:
        print(f"MongoDB存储失败: {str(e)}")
        print(f"MongoDB存储失败: {str(e)}")


def generate_css_selector(comment_div):
    try:
        # 首先找到回复按钮元素
        reply_button = comment_div.find('div', class_=['reply', 'icon-container']).find('span', class_='count')
        if not reply_button:
            print("未找到回复按钮元素")
            return None

        # 构建元素的完整路径
        path_parts = []
        current = reply_button

        # 向上遍历DOM树直到body元素
        while current and current.name and current.name != 'body':
            # 获取所有同类型的兄弟节点（包括当前节点）
            siblings = current.parent.find_all(current.name, recursive=False)

            # 只有当存在多个同级元素时才添加索引
            if len(siblings) > 1:
                # 找出当前节点在所有兄弟节点中的位置
                position = next((i + 1 for i, sibling in enumerate(siblings) if sibling is current), 1)
                path_parts.append(f"{current.name}[{position}]")
            else:
                path_parts.append(current.name)

            current = current.parent

        # 添加body和html
        path_parts.append('body')
        path_parts.append('html')

        # 反转路径并组合成完整的xpath
        xpath = '/html/' + '/'.join(reversed(path_parts[:-1]))  # 去掉多余的html
        return xpath

    except Exception as e:
        print(f"生成XPath时出错: {str(e)}")
        return None


def is_within_days(comment_date_str: str, days: int = 3) -> bool:
    """
    判断评论时间是否在指定天数内

    Args:
        comment_date_str (str): 评论时间字符串，格式如 '2024-03-21'
        days (int): 天数限制，默认3天

    Returns:
        bool: 在指定天数内返回True，否则返回False
    """
    try:
        # 如果格式是 "3 天前"，则转换为当前时间减去3天
        if re.match(r'\d+ 天前', comment_date_str):
            days_ago = int(comment_date_str.split()[0])
            comment_date = datetime.now() - timedelta(days=days_ago)
            return comment_date <= datetime.now()
        # 如果是"昨天"开头的，则转换为当前时间减去1天
        elif re.match(r'昨天', comment_date_str):
            comment_date = datetime.now() - timedelta(days=1)
            return comment_date <= datetime.now()
        # 如果是"今天"开头的，则转换为当前时间
        elif re.match(r'今天', comment_date_str):
            comment_date = datetime.now()
            return comment_date <= datetime.now()

        # 如果时间格式是01-03这样的，则转换为2024-01-03，其中2024替换为当前年
        if re.match(r'\d{2}-\d{2}', comment_date_str):
            current_year = datetime.now().year
            comment_date_str = f"{current_year}-{comment_date_str}"

        # 判断时间格式是不是2024-03-21这样的
        if not re.match(r'\d{4}-\d{2}-\d{2}', comment_date_str):
            print(f"日期格式错误: {comment_date_str}")
            return True
        comment_date = datetime.strptime(comment_date_str, '%Y-%m-%d')
        current_date = datetime.now()
        date_diff = current_date - comment_date
        return date_diff.days <= days
    except Exception as e:
        print(f"日期解析错误: {str(e)}")
        return True  # 如果解析失败，默认保留该评论


# 新增示例使用函数
def parse_note_from_file(file_path):
    """
    从文件读取HTML内容并解析小红书笔记

    Args:
        file_path (str): HTML文件路径

    Returns:
        str: JSON格式的解析结果
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return parse_xhs_note(html_content)
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        return f"错误: {str(e)}"


def test_mongodb_connection():
    """
    测试MongoDB连接是否正常
    Returns:
        bool: 连接成功返回True，失败返回False
    """
    try:
        collection = get_mongodb_connection()
        if collection is not None:
            # 尝试执行一个简单的查询来验证连接
            collection.find_one()
            print("MongoDB连接测试成功")
            return True
        else:
            print("MongoDB连接获取失败")
            return False
    except Exception as e:
        print(f"MongoDB连接测试失败: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    pass
    # 从文件读取
    file_path = "D:/your_html_file.html"  # 替换为实际的HTML文件路径
    result = parse_note_from_file(file_path)
    print(result)

# # 或者直接传入HTML字符串
# html_content = """
# <你的HTML内容>
# """
# result = parse_xhs_note(html_content)
# print(result)

# 测试MongoDB连接
# if test_mongodb_connection():
#     print("MongoDB连接正常")
# else:
#     print("MongoDB连接失败")

