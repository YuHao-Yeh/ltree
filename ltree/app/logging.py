# ltree/app/logging.py
from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO


class CliFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if record.levelno >= logging.ERROR:
            return f"Error: {record.getMessage()}"

        if record.levelno >= logging.WARNING:
            return f"Warning: {record.getMessage()}"

        return record.getMessage()


def configure_logging(stream: TextIO | None = None) -> None:
    logger = logging.getLogger("ltree")
    if logger.handlers:
        return

    stream = stream or sys.stderr
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(CliFormatter())

    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    logger.propagate = False
