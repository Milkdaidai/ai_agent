"""FastAPI 主应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.config import settings
from app.core.logging import setup_logging

# dev 提交测试
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    在应用启动时执行初始化（如配置日志）。

    Args:
        app: FastAPI 应用实例。
    """
    setup_logging()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
