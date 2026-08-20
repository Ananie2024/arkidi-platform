"""
Structured JSON and Console Logging Configuration
"""
import logging
import os
import sys
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging() -> logging.Logger:
    """Configures application-wide structured logger."""
    logger = logging.getLogger("arkidi")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # JSON File Handler
    try:
        log_dir = os.path.dirname(settings.LOG_FILE_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8")
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s"
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not initialize file log handler: {e}")

    return logger
