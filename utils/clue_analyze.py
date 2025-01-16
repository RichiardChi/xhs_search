
import requests
import os
import json
import hashlib
from pymongo import MongoClient, UpdateOne
import traceback
from datetime import datetime
glv = {}
with open(os.path.join(os.getcwd(),'xhs_rpa_config.txt'), 'r', encoding='utf-8') as file:
    glv = json.load(file)
    print('配置文件：', glv)
default_system_prompt = """
[角色]
你是一个商机挖掘人员，擅长从从互联网平台的聊天内容中发现可以进行开展信用卡服务推广的线索。
[任务]
你会得到一篇发标在互联网上的文章，以及针对这篇文章的评论列表，其中，每一条评论下面又可能存在子级评论，格式如下：
```
{
	"_id": "文章的唯一标识",
	"note_title": "文章的标题",
    "note_url": "文章的链接",
	"note_author": "文章的作者",
	"note_content": "文章的正文",
    "follow_time": "文章的抓取时间",
	"comment_list":
	[
		{
			"nick_name": "用户名",
			"comment_content": "评论内容",
			"comment_time": "评论时间",
            "reply_button_selector": "回复按钮的selector",
            "need_to_follow": "是否需要跟进，0表示不需要跟进，1表示需要跟进",
            "location": "评论者所在城市",
			"comment_list":
			[
				{
					"nick_name": "用户名",
					"comment_content": "评论内容",
					"comment_time": "评论时间",
                    "reply_button_selector": "回复按钮的selector",
                    "need_to_follow": "是否需要跟进，0表示不需要跟进，1表示需要跟进",
                    "location": "评论者所在城市"
				},
				{
					"nick_name": "用户名",
					"comment_content": "评论内容",
					"comment_time": "评论时间",
                    "reply_button_selector": "回复按钮的selector",
                    "need_to_follow": "是否需要跟进，0表示不需要跟进，1表示需要跟进",
                    "location": "评论者所在城市"
				}
			]
		},

		{
			"nick_name": "用户名",
			"comment_content": "评论内容",
			"comment_time": "评论时间",
            "reply_button_selector": "回复按钮的selector",
			"comment_list":
			[
				{
					"nick_name": "用户名",
					"comment_content": "评论内容",
					"comment_time": "评论时间",
                    "reply_button_selector": "回复按钮的selector",
                    "need_to_follow": "是否需要跟进，0表示不需要跟进，1表示需要跟进",
                    "location": "评论者所在城市"
				},
				{
					"nick_name": "用户名",
					"comment_content": "评论内容",
					"comment_time": "评论时间",
                    "reply_button_selector": "回复按钮的selector",
                    "need_to_follow": "是否需要跟进，0表示不需要跟进，1表示需要跟进",
                    "location": "评论者所在城市"
				}
			]
		}

	]
}
```
请结合文章主题、内容和用户的评论，遵循给定的规则，一步步发掘出你认为对信用卡存在潜在需求的用户及其发表的评论。

[分析步骤]
第一步：首先过滤掉所有不符合基本条件的评论：
1. 被标记为不需要跟进，也就是need_to_follow为0的评论评论时间距今超过7天的评论必须立即排除，不进行后续分析。
2. 
3. 评论者为商家的评论
4. 评论者已有广发银行信用卡的评论
5. 对信用卡表现出明显反感的评论

第二步：在剩余的评论中，如果出现以下情况可以认为用户有潜在信用卡需求：
1. 评论内容包含以下关键字：[有免年费的吗，能办visa卡吗、想办visa卡、要有积分可以换里程，要有贵宾厅、广发笔笔返、要有高铁贵宾厅、有机场贵宾厅吗、有龙腾贵宾厅吗、有无限贵宾厅、不限次数、是广发的吗，广发都有什么权益、想要办广发白金卡、求广发信用卡推荐、线上能办吗、有返现吗、办一张备用卡、有多少立减金、广发什么卡、信用卡怎么办、国外能用吗、有年费吗、办卡有礼品吗、我想办张信用卡、我要办信用卡、打算去申请信用卡了、哪个信用卡比较好办理呀、急需一张信用卡来周转资金、这两天就要办、马上要出去旅游了、广州能办吗、想办visa卡、出国办什么卡]
2. 明确表达出希望办理信用卡或咨询信用卡相关问题
第三步：按照[线索有效性评估维度]评估线索有效性，每个维度0~5分，分数越高代表线索越有效。按照各维度得分总和进行排序，最终给出score不低于75分的评论，数量不超过5条。
第四步：按照[输出格式要求]输出结果。

[线索有效性评估维度]
1.用户是否表达出明确的办理信用卡的意愿
2.对使用信用卡进行消费的接受程度
3.对信用卡的需求急迫性
4.发标评论的时间距离现在是否很长，越久之前的线索价值越低

[输出格式要求]
请按照[线索有效性评估维度]评估线索有效性，每个维度0~5分，分数越高代表线索越有效。按照各维度得分总和进行排序，最终给出score不低于75分的评论，数量不超过5条，并将评论以JSON数组的形式输出给我，请注意输出的内容不要换行。当你认为没有符合条件的评论时，输出一个空字符串数组。
输出格式如下：

[
	{
		"note_title": "所属文章标题",
		"nick_name": "用户名",
		"content": "评论内容",
		"location": "评论者所在城市",
		"reply_time": "评论时间",
        "reply_button_selector": "回复按钮的selector",
		"reason": "认为是有效线索的原因，如：'客户希望能够在订酒店时获得优惠'",
		"score": "线索有效性评估维度的总得分除以总分的占比，例如得分18，总分是20，则输出90"
	},
	{
		"note_title": "所属文章标题",
		"nick_name": "用户名",
		"content": "评论内容",
		"location": "评论者所在城市",
		"reply_time": "评论时间",
        "reply_button_selector": "回复按钮的selector",
		"reason": "认为是有效线索的原因，如：'客户希望能够在订酒店时获得优惠'",
		"score": "线索有效性评估维度的总得分除以总分的占比，例如得分14，总分是20，则输出70"
	}
]

[重点强调]
1.全部内容在一行输出
2.不要输出分析过程等内容，只需要输出结果数组
3.如果一个用户多次评论，则只输出一条你认为需求意向最强烈的评论。

以下是给你分析的内容：


"""

"""
    调用llm模型的API

    Args:
        xhs_note_json_str (str): 用户的问题
        system_prompt (str, optional): 系统提示词。默认为"You are a helpful assistant."

    Returns:
        str: 模型的回答

    Raises:
        Exception: 如果API调用失败，将抛出异常
    """


def ask_llm(xhs_note_json_str: str) -> list:
    system_prompt = default_system_prompt

    llm_config = glv['llm_config']

    base_url = llm_config['base_url'] if 'base_url' in llm_config else "https://api.deepseek.com"
    model_name = llm_config['model_name'] if 'model_name' in llm_config else "deepseek-chat"

    api_key = llm_config['api_key']
    if not api_key:
        raise ValueError("请配置 API_KEY")

    url = base_url + "/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        # 构建请求数据
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": default_system_prompt
                },
                {
                    "role": "user",
                    "content": xhs_note_json_str
                }
            ]
        }

        # 发送请求
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"API原始返回内容: {content}")
        # 对结果进行处理确保是有效的JSON数组格式
        clue_list_str = sanitize_json_array(content)
        clue_list = json.loads(clue_list_str)

        # 将xhs_note_json_str（待分析的评论列表）转换为json对象
        xhs_note_json = json.loads(xhs_note_json_str, strict=False)

        # 记录已跟进用户，将clue_json_array中的用户名抽取出来，组成一个user_list
        user_list = []
        for clue in clue_list:
            user_list.append({
                "_id": hashlib.md5(clue["nick_name"].encode('utf-8')).hexdigest(),
                "nick_name": clue["nick_name"],
                "reply_time": clue["reply_time"],
                "note_id": xhs_note_json["_id"],
                "note_title": xhs_note_json["note_title"],
                "note_url": xhs_note_json["note_url"],
                "reply_content": clue["content"],
                "reason": clue["reason"],
                "score": clue["score"]
            })

        record_followed_users_to_mongodb(user_list)

        # 记录已跟进线索

        # 对线索列表进行循环，将文章信息和线索信息合并
        for clue in clue_list:
            # 将文章ID和用户名组装起来作为clue的唯一id，为了防止用户名有特殊字符，对组装后的字符串进行md5加密
            clue["_id"] = hashlib.md5((xhs_note_json["_id"] + clue["nick_name"]).encode('utf-8')).hexdigest()
            clue["note_id"] = xhs_note_json["_id"]
            clue["note_title"] = xhs_note_json["note_title"]
            clue["note_link"] = xhs_note_json["note_url"]
            clue["note_content"] = xhs_note_json["note_content"]

        record_followed_clues_to_mongodb(clue_list)

        return clue_list

    except Exception as e:
        raise Exception(f"调用API失败: {str(e)}, {traceback.print_exc()}")


def record_followed_clues_to_mongodb(clue_list: list) -> None:
    """
    记录已跟进的用户到MongoDB中
    """
    if clue_list is None or len(clue_list) == 0:
        return
    connection = get_mongodb_connection(db_name="xhs_note", collection_name="followed_clues")
    if connection is not None:
        operations = [
            UpdateOne(
                {'_id': clue['_id']},  # 查询条件
                {'$set': clue},  # 更新内容
                upsert=True  # 不存在则插入
            ) for clue in clue_list
        ]
        result = connection.bulk_write(operations)
        print(f"更新{result.modified_count}条线索，插入{result.upserted_count}条线索")
    else:
        print("记录已跟进线索到MongoDB失败，原因：connection is None")


def record_followed_users_to_mongodb(user_list: list) -> None:
    """
    记录已跟进的用户到MongoDB中
    """
    if user_list is None or len(user_list) == 0:
        return
    connection = get_mongodb_connection(db_name="xhs_note", collection_name="followed_users")
    if connection is not None:
        # 使用批量更新操作
        operations = [
            UpdateOne(
                {'_id': user['_id']},  # 查询条件
                {'$set': user},  # 更新内容
                upsert=True  # 不存在则插入
            ) for user in user_list
        ]
        result = connection.bulk_write(operations)
        print(f"更新{result.modified_count}条用户数据，插入{result.upserted_count}条用户数据")
    else:
        print("记录已跟进用户到MongoDB失败，原因：connection is None")


def sanitize_json_array(text: str) -> str:
    """
    确保返回的字符串是一个有效的JSON数组格式
    即以'['开头，以']'结尾
    """
    # 找到第一个'['的位置
    start_pos = text.find('[')
    if start_pos == -1:
        return '[]'  # 如果没有找到'['，返回空数组

    # 从后向前找到最后一个']'的位置
    end_pos = text.rfind(']')
    if end_pos == -1:
        return '[]'  # 如果没有找到']'，返回空数组

    # 提取有效的JSON数组部分
    result = text[start_pos:end_pos + 1]

    # 验证是否为有效的JSON数组
    try:
        parsed = json.loads(result, strict=False)
        if not isinstance(parsed, list):
            glv['llm_error_times'] = glv['llm_error_times'] + 1
            print("llm返回的格式不是数组，请关注")
            return '[]'
        return result
    except json.JSONDecodeError:
        glv['llm_error_times'] = glv['llm_error_times'] + 1
        print("llm返回的格式不是json格式，请关注")
        return '[]'


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
        return None


# 使用示例
if __name__ == "__main__":
    pass