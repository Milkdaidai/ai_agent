"""大模型封装（基于 LangChain）"""

from app.llm.base import BaseLLM
from app.core.config import settings
from app.core.exceptions import ConfigError


class LLMFactory:
    """LLM 工厂，根据配置创建 LangChain ChatModel 实例"""

    _providers = {
        "openai": lambda: BaseLLM(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        ),
        "deepseek": lambda: BaseLLM(
            model="deepseek-chat",
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        ),
        "ollama": lambda: BaseLLM(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key="ollama",
            base_url=settings.OLLAMA_BASE_URL + "/v1",
        ),
    }

    @classmethod
    def create(cls) -> "ChatOpenAI":
        """根据配置创建 LangChain ChatModel 实例

        Returns:
            ChatOpenAI（或兼容的 ChatModel）实例。

        Raises:
            ConfigError: 不支持的 provider 时抛出。
        """
        provider = settings.LLM_PROVIDER
        builder = cls._providers.get(provider)
        if not builder:
            raise ConfigError(f"不支持的 LLM provider: {provider}")
        return builder().build()
