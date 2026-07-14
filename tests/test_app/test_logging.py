# tests/test_app/test_logging.py
from __future__ import annotations

import io
import logging
import pytest

from ltree.app.logging import CliFormatter, configure_logging


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture(autouse=True)
def reset_logger():
    logger = logging.getLogger("ltree")

    handlers = logger.handlers[:]
    level = logger.level
    propagate = logger.propagate

    logger.handlers.clear()

    yield logger

    logger.handlers.clear()
    logger.handlers.extend(handlers)
    logger.setLevel(level)
    logger.propagate = propagate


def make_record(level: int, msg: str, *args):
    return logging.LogRecord(
        name="ltree",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


# ======================================================================= #
# Tests: CliFormatter
# ======================================================================= #
def test_formatter_info():
    formatter = CliFormatter()
    record = make_record(logging.INFO, "hello")
    assert formatter.format(record) == "hello"


def test_formatter_warning():
    formatter = CliFormatter()
    record = make_record(logging.WARNING, "hello")
    assert formatter.format(record) == "Warning: hello"


def test_formatter_error():
    formatter = CliFormatter()
    record = make_record(logging.ERROR, "hello")
    assert formatter.format(record) == "Error: hello"


def test_formatter_critical():
    formatter = CliFormatter()
    record = make_record(logging.CRITICAL, "hello")
    assert formatter.format(record) == "Error: hello"


def test_formatter_formats_arguments():
    formatter = CliFormatter()
    record = make_record(
        logging.WARNING,
        "hello %s",
        "world",
    )
    assert formatter.format(record) == "Warning: hello world"


# ======================================================================= #
# Tests: configure_logging()
# ======================================================================= #
def test_configure_logging_adds_handler():
    logger = logging.getLogger("ltree")

    assert logger.handlers == []

    configure_logging()

    assert len(logger.handlers) == 1


def test_configure_logging_sets_formatter():
    configure_logging()

    logger = logging.getLogger("ltree")
    handler = logger.handlers[0]

    assert isinstance(handler.formatter, CliFormatter)


def test_configure_logging_sets_level():
    configure_logging()

    logger = logging.getLogger("ltree")

    assert logger.level == logging.WARNING


def test_configure_logging_sets_propagate():
    configure_logging()

    logger = logging.getLogger("ltree")

    assert logger.propagate is False


def test_configure_logging_uses_given_stream():
    stream = io.StringIO()

    configure_logging(stream)

    logger = logging.getLogger("ltree")
    handler = logger.handlers[0]

    assert handler.stream is stream


def test_configure_logging_is_idempotent():
    logger = logging.getLogger("ltree")

    configure_logging()

    assert len(logger.handlers) == 1


def test_logger_warning_output():
    stream = io.StringIO()

    configure_logging(stream)

    logger = logging.getLogger("ltree")
    logger.warning("hello")

    assert stream.getvalue() == "Warning: hello\n"


def test_logger_error_output():
    stream = io.StringIO()

    configure_logging(stream)

    logger = logging.getLogger("ltree")
    logger.error("boom")

    assert stream.getvalue() == "Error: boom\n"


def test_logger_info_not_output():
    stream = io.StringIO()

    configure_logging(stream)

    logger = logging.getLogger("ltree")
    logger.info("hello")

    assert stream.getvalue() == ""
