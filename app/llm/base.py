"""LLM 抽象基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """LLM 响应数据类

    Attributes:
        content: LLM 返回的文本内容。
        tool_calls: LLM 返回的工具调用列表。
    """
    content: str | None = None
    tool_calls: list[Any] | None = None


class BaseLLM(ABC):
    """LLM 抽象基类，定义统一的聊天接口"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """调用 LLM 聊天接口（抽象方法）

        Args:
            messages: 消息列表。
            tools: OpenAI 格式的工具定义列表。
            temperature: 生成温度。
            max_tokens: 最大生成 Token 数。

        Returns:
            LLMResponse 对象。
        """
        ...
