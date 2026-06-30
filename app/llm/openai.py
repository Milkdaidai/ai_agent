"""OpenAI LLM 实现"""

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM, LLMResponse


class OpenAILLM(BaseLLM):
    """OpenAI LLM 实现，使用 OpenAI SDK 调用 GPT 系列模型"""

    def __init__(self):
        """初始化 OpenAI 客户端

        从配置中读取 API Key 和 Base URL，创建 AsyncOpenAI 客户端。
        """
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    async def chat(self, messages, tools=None, temperature=0.7, max_tokens=4096):
        """调用 OpenAI 聊天接口

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
