"""
core.logging_config
===================

Centralized logging configuration for the event router.

This module configures structured, stdout-based logging suitable for:
- Docker
- Kubernetes
- Log aggregation systems (ELK, Loki, CloudWatch)

It supports structured metadata via the `extra` argument on log calls.
"""

import logging
import sys
from typing import Any, Dict


class SafeExtraFormatter(logging.Formatter):
    """
    Logging formatter that safely renders `extra` fields.

    Any attributes attached via the `extra` argument will be
    automatically appended to the log output as key=value pairs.
    """

    STANDARD_ATTRS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with structured extra fields.

        Parameters
        ----------
        record : logging.LogRecord
            Log record instance.

        Returns
        -------
        str
            Formatted log message.
        """
        base_message = super().format(record)

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.STANDARD_ATTRS
        }

        if not extras:
            return base_message

        extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
        return f"{base_message} | {extra_str}"


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide logging.

    Parameters
    ----------
    log_level : str, optional
        Logging level (e.g. DEBUG, INFO, WARNING), by default "INFO".
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        SafeExtraFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
