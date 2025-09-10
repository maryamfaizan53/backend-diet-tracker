# py
from loguru import logger
import sys
from app.core.config import get_settings

def configure_logging(level: str):
    logger.remove()
    logger.add(sys.stderr, level=level, format="{time} {level} {message}", serialize=False)
    logger.info("Logging configured", level=level)
