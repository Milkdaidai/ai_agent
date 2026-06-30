"""Agent 核心逻辑"""

from typing import Any

from app.core.config import settings
from app.agent.prompt import system_prompt
from app.agent.memory import Memory
from app.agent.tools import ToolRegistry
from app.llm import LLMFactory
from app.schemas.chat import Message


class Agent:
    def __init__(self):
        self.memory = Memory()
        self.tools = ToolRegistry()
        self.llm = LLMFactory.create(settings.LLM_PROVIDER)

    async def run(self, messages: list[Message]) -> str:
        self.memory.add_messages(messages)

        full_messages = [
            {"role": "system", "content": system_prompt},
            *self.memory.get_messages(),
        ]

        response = await self.llm.chat(
            messages=full_messages,
            tools=self.tools.get_tool_definitions(),
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        if response.tool_calls:
            return await self._handle_tool_calls(response, full_messages)

        return response.content or ""

    async def _handle_tool_calls(self, response: Any, messages: list[dict]) -> str:
        for tc in response.tool_calls:
            result = await self.tools.execute(tc.function.name, tc.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        final = await self.llm.chat(messages=messages)
        return final.content or ""
