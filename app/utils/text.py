"""文本工具"""

import re

# 本地main提交到远程dev
def truncate(text: str, max_length: int = 2000) -> str:
    """截断文本到指定长度

    Args:
        text: 原始文本。
        max_length: 最大长度，默认为 2000。

    Returns:
        截断后的文本，超过部分以 "..." 替代。
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def remove_extra_whitespace(text: str) -> str:
    """移除文本中的多余空白字符

    将连续空白替换为单个空格，并去除首尾空格。

    Args:
        text: 原始文本。

    Returns:
        处理后的文本。
    """
    return re.sub(r"\s+", " ", text).strip()
