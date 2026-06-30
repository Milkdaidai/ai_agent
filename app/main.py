"""FastAPI 主应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
