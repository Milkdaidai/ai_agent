"""LLM 抽象基类（基于 LangChain）"""

from langchain_core.language_models import BaseChatModel


class BaseLLM:
    """LLM 包装类，封装 LangChain ChatModel 的创建"""

    def __init__(self, model: str, temperature: float, api_key: str, base_url: str):
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.base_url = base_url

    def build(self) -> BaseChatModel:
        """创建 LangChain ChatModel 实例"""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=self.api_key,
            base_url=self.base_url,
        )
