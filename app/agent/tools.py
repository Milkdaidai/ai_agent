"""工具注册与调度（基于 LangChain @tool）

每个工具使用 LangChain 的 @tool 装饰器定义，自动生成
JSON Schema（Function Calling 格式）。本模块负责将散落在
tools/ 目录下的工具汇集为一个列表，供 Agent 绑定。
"""

from app.tools.weather import get_weather
from app.tools.search import web_search
from app.tools.db import query_database
from app.tools.browser import browse


def get_tool_registry() -> list:
    """获取所有已注册的 LangChain 工具列表

    LangGraph 和 LLM 通过 bind_tools() 消费此列表，
    自动获得工具的 JSON Schema 定义。

    Returns:
        LangChain tool 对象列表，每个对象包含 name、description、args_schema 等。
    """
    return [get_weather, web_search, query_database, browse]
