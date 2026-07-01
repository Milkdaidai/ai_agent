"""应用配置

通过 pydantic-settings 从 .env 和环境变量加载所有配置项。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，从 .env 和环境变量加载配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ── LLM 配置 ────────────────────────────────────────
    LLM_PROVIDER: str = "openai"       # 可选: openai / deepseek / ollama
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # ── 各供应商 API Key / 主机地址 ──────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ── 工具配置 ────────────────────────────────────────
    OPENWEATHER_API_KEY: str = ""

    # ── 数据库 ──────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./data/agent.db"

    # ── 缓存 / 状态持久化 ───────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
