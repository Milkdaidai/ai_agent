"""工具相关 Pydantic 模型"""

from pydantic import BaseModel


class ToolCall(BaseModel):
    """工具调用请求模型"""

    id: str
    name: str
    arguments: str


class ToolResult(BaseModel):
    """工具调用结果模型"""

    tool_call_id: str
    content: str
