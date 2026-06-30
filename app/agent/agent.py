"""Agent 核心逻辑"""

from typing import Any

from app.core.config import settings
from app.agent.prompt import system_prompt
from app.agent.memory import Memory
from app.agent.tools import ToolRegistry
from app.llm import LLMFactory
from app.schemas.chat import Message


class Agent:
    """Agent 主类，负责管理对话生命周期"""

    def __init__(self):
        """初始化 Agent，创建记忆、工具注册表和 LLM 实例"""
        self.memory = Memory()
        self.tools = ToolRegistry()
        self.llm = LLMFactory.create(settings.LLM_PROVIDER)

    async def run(self, messages: list[Message]) -> str:
        """运行 Agent 主循环

        接收用户消息，调用 LLM 生成回复。
        如果 LLM 返回工具调用，则执行工具并再次调用 LLM 获取最终回复。

        Args:
            messages: 用户消息列表。

        Returns:
            LLM 生成的回复文本。
        """
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
        """处理工具调用结果

        依次执行每个工具，将结果追加到消息列表中，
        然后再次调用 LLM 获取基于工具结果的最终回复。

        Args:
            response: LLM 返回的包含工具调用的响应。
            messages: 当前消息列表。

        Returns:
            最终回复文本。
        """
        for tc in response.tool_calls:
            result = await self.tools.execute(tc.function.name, tc.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        final = await self.llm.chat(messages=messages)
        return final.content or ""
