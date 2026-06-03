# utils/logger.py
"""
Centralized logging utility for MedChain EMR System.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger
    """
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"medchain_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
