"""Logging configuration for JARVIS."""

import logging
import sys
from pathlib import Path
from typing import Literal

from .config import LOG_LEVEL, LOG_PATH


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Create and configure a logger with console and file handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Override log level (defaults to LOG_LEVEL from config)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    effective_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, effective_level.upper()))
    
    if logger.handlers:
        return logger
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    log_file = LOG_PATH / "jarvis.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger
