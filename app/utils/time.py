"""时间工具"""

from datetime import datetime, timezone


def now_utc() -> datetime:
    """获取当前 UTC 时间

    Returns:
        当前 UTC 时间。
    """
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime | None = None) -> str:
    """格式化时间戳为字符串

    Args:
        dt: 日期时间对象，默认为当前时间。

    Returns:
        格式化后的时间字符串（YYYY-MM-DD HH:MM:SS）。
    """
    dt = dt or now_utc()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
