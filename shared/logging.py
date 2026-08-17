from __future__ import annotations

import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)


class StructuredLogger:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def info(self, message: str, **fields: Any) -> None:
        self._logger.info(message, extra=fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._logger.warning(message, extra=fields)

    def error(self, message: str, **fields: Any) -> None:
        self._logger.error(message, extra=fields)

    def exception(self, message: str, **fields: Any) -> None:
        self._logger.exception(message, extra=fields)


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(logging.getLogger(name))
