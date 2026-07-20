"""Centralized logging configuration for ForgeCLI."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_CONFIGURED = False


def get_log_dir() -> Path:
    """Return the directory where ForgeCLI stores its logs, creating it if needed."""
    base = os.environ.get("FORGECLI_HOME") or str(Path.home() / ".forgecli")
    log_dir = Path(base) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def configure_logging(level: Optional[str] = None, file_logging: bool = True) -> logging.Logger:
    """Configure root logging once. Returns the ``forgecli`` logger."""
    global _CONFIGURED
    logger = logging.getLogger("forgecli")

    if _CONFIGURED:
        return logger

    env_level = os.environ.get("FORGECLI_LOG_LEVEL", "INFO").upper()
    resolved = (level or env_level)
    numeric = getattr(logging, resolved, logging.INFO)
    logger.setLevel(numeric)

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)  # keep console quiet; UI handles user messaging
    console.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    logger.addHandler(console)

    if file_logging:
        try:
            file_handler = logging.FileHandler(get_log_dir() / "forgecli.log", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
            logger.addHandler(file_handler)
        except OSError:
            # File logging is a nicety, never a hard requirement.
            pass

    logger.propagate = False
    _CONFIGURED = True
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``forgecli`` namespace."""
    configure_logging()
    return logging.getLogger(f"forgecli.{name}")