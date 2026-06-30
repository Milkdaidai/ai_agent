"""工具相关 Pydantic 模型"""

from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class ToolResult(BaseModel):
    tool_call_id: str
    content: str
