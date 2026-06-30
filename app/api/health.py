"""健康检查接口"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """健康检查接口

    Returns:
        状态信息。
    """
    return {"status": "ok"}
