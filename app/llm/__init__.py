"""大模型封装，提供 LLM 工厂和多种实现"""

from app.llm.base import BaseLLM
from app.llm.openai import OpenAILLM
from app.llm.deepseek import DeepSeekLLM
from app.llm.ollama import OllamaLLM
from app.core.exceptions import ConfigError


class LLMFactory:
    """LLM 工厂类，根据配置创建对应供应商的 LLM 实例"""

    _providers = {
        "openai": OpenAILLM,
        "deepseek": DeepSeekLLM,
        "ollama": OllamaLLM,
    }

    @classmethod
    def create(cls, provider: str) -> BaseLLM:
        """根据提供商名称创建 LLM 实例

        Args:
            provider: LLM 提供商名称（openai / deepseek / ollama）。

        Returns:
            BaseLLM 子类实例。

        Raises:
            ConfigError: 不支持的 provider 时抛出。
        """
        llm_cls = cls._providers.get(provider)
        if not llm_cls:
            raise ConfigError(f"不支持的 LLM provider: {provider}")
        return llm_cls()
