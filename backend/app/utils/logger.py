"""结构化日志配置 — 基于 Loguru"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(debug: bool = False) -> None:
    """初始化 Loguru 日志配置"""
    # 移除默认 handler
    logger.remove()

    # 控制台输出：开发环境彩色
    if debug:
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}:{function}:{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
        )
    else:
        # 生产环境：JSON 序列化到控制台
        logger.add(
            sys.stdout,
            serialize=True,
            level="INFO",
        )

    # 文件输出：始终 JSON 序列化
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        str(log_dir / "app_{time:YYYY-MM-DD}.log"),
        serialize=True,
        level="DEBUG",
        rotation="00:00",
        retention="30 days",
        compression="gz",
    )

    logger.info(f"Logger initialized (debug={debug})")
