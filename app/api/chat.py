"""聊天接口"""

from fastapi import APIRouter, Depends

from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.agent import Agent

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口

    接收用户消息，交给 Agent 处理，返回 LLM 的回复。

    Args:
        request: 聊天请求，包含消息列表。

    Returns:
        包含 LLM 回复的响应。
    """
    agent = Agent()
    response = await agent.run(request.messages)
    return ChatResponse(reply=response)
