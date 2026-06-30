"""聊天接口"""

from fastapi import APIRouter, Depends

from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.agent import Agent

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    agent = Agent()
    response = await agent.run(request.messages)
    return ChatResponse(reply=response)
