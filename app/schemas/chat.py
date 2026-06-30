"""聊天相关 Pydantic 模型"""

from pydantic import BaseModel


class Message(BaseModel):
    """单条消息模型"""

    role: str
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""

    messages: list[Message]


class ChatResponse(BaseModel):
    """聊天响应模型"""

    reply: str
