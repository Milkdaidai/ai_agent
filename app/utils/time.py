"""时间工具"""

from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime | None = None) -> str:
    dt = dt or now_utc()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
