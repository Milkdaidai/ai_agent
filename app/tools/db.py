"""数据库查询工具"""


async def query_database(sql: str) -> str:
    """执行 SQL 查询"""
    return f"数据库查询功能待实现。SQL: {sql}"


DB_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "查询本地数据库",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL 查询语句"},
            },
            "required": ["sql"],
        },
    },
}
