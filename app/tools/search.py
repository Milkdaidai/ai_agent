"""搜索工具"""

from langchain_core.tools import tool


@tool
async def web_search(query: str) -> str:
    """搜索互联网信息（需配置搜索 API）

    Args:
        query: 搜索关键词。
    """
    return f"搜索功能待配置。查询: {query}"
