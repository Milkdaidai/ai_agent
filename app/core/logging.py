"""日志配置"""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """配置日志格式和输出

    设置统一的日志格式（时间、级别、模块名、消息），
    输出到标准输出。

    Args:
        level: 日志级别，默认为 INFO。
    """
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
