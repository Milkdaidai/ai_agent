"""应用配置"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # LLM 配置
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # 各 provider API Key / 主机地址
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/agent.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
