"""大模型封装"""

from app.llm.base import BaseLLM
from app.llm.openai import OpenAILLM
from app.llm.deepseek import DeepSeekLLM
from app.llm.ollama import OllamaLLM
from app.core.exceptions import ConfigError


class LLMFactory:
    _providers = {
        "openai": OpenAILLM,
        "deepseek": DeepSeekLLM,
        "ollama": OllamaLLM,
    }

    @classmethod
    def create(cls, provider: str) -> BaseLLM:
        llm_cls = cls._providers.get(provider)
        if not llm_cls:
            raise ConfigError(f"不支持的 LLM provider: {provider}")
        return llm_cls()
