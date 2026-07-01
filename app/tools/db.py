"""数据库查询工具"""

from langchain_core.tools import tool


@tool
async def query_database(sql: str) -> str:
    """执行 SQL 查询

    Args:
        sql: SQL 查询语句。
    """
    return f"数据库查询功能待实现。SQL: {sql}"
