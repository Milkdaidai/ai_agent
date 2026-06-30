"""Ollama LLM 实现"""

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM, LLMResponse


class OllamaLLM(BaseLLM):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key="ollama",
            base_url=settings.OLLAMA_BASE_URL + "/v1",
        )
        self.model = settings.LLM_MODEL

    async def chat(self, messages, tools=None, temperature=0.7, max_tokens=4096):
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
