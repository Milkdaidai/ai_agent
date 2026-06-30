"""DeepSeek LLM 实现"""

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM, LLMResponse


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM 实现，使用 OpenAI 兼容的 SDK 调用 DeepSeek 模型"""

    def __init__(self):
        """初始化 DeepSeek 客户端

        从配置中读取 API Key 和 Base URL，使用 OpenAI 兼容的 SDK 创建客户端。
        """
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = "deepseek-chat"

    async def chat(self, messages, tools=None, temperature=0.7, max_tokens=4096):
        """调用 DeepSeek 聊天接口

        Args:
            messages: 消息列表。
            tools: OpenAI 格式的工具定义列表。
            temperature: 生成温度。
            max_tokens: 最大生成 Token 数。

        Returns:
            LLMResponse 对象。
        """
        kwargs = dict(model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        if tools:
            kwargs["tools"] = tools

        resp = await self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        msg = choice.message

        return LLMResponse(
            content=msg.content,
            tool_calls=msg.tool_calls,
        )
