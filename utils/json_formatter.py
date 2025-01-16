import json

def format_clue_list_to_str(clue_list):
    """
    将线索列表转换为格式化的字符串，用于发送给用户阅读

    Args:
        clue_list (list): 包含线索字典的列表

    Returns:
        str: 格式化后的字符串
    """
    result = []
    for clue in clue_list:
        clue_str = (
            f"用户名：{clue['nick_name']}\n"
            f"评论内容：{clue['content']}\n"
            f"评论时间：{clue['reply_time']}\n"
            f"线索分析：{clue['reason']}\n"
            f"线索得分（满分100分）：{clue['score']}\n"
            "------------------------"
        )
        result.append(clue_str)

    return "\n".join(result)