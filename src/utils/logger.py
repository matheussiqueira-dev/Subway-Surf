from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_FILE_NAME = "subway-controller.log"
_MAX_BYTES = 1_048_576  # 1 MiB
_BACKUP_COUNT = 3


def configure_logging(log_level: str, log_dir: Path) -> None:
    """Configure the root logger with a rotating file handler and a stderr stream handler.

    Both handlers share the same formatter so log output is consistent
    regardless of where it is consumed (terminal vs log file).

    Args:
        log_level: One of DEBUG / INFO / WARNING / ERROR / CRITICAL (case-insensitive).
                   Defaults to INFO when the string is not recognised.
        log_dir:   Directory for the rotating log file; created if absent.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        filename=log_dir / _FILE_NAME,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
