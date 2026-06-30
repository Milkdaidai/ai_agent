"""搜索工具"""

import httpx


async def web_search(query: str) -> str:
    """执行网络搜索（需配置搜索 API）"""
    return f"搜索功能待配置。查询: {query}"


SEARCH_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "搜索互联网信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
            },
            "required": ["query"],
        },
    },
}
