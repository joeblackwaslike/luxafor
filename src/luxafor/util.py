import sys
from loguru import logger


def setup_logger():
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        level="INFO",
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        serialize=True
    )
    # logger.disable("luxafor")
    return logger