"""文本工具"""

import re


def truncate(text: str, max_length: int = 2000) -> str:
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def remove_extra_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
