"""日志配置"""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
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
