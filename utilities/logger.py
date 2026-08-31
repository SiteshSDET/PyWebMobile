"""
logger.py

Centralized logging utility for the automation framework.
"""

from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = (
    Path(__file__).resolve().parent.parent / "logs"
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "automation.log"


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    The logger writes to:
        - Console
        - logs/automation.log
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger