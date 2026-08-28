from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import structlog

_SECRET_KEYS = {"password", "token", "access_token", "auth_token", "secret", "authorization"}


def sanitize_log_data(value: object) -> object:
    """Redact secrets from nested dicts before logging."""
    if isinstance(value, dict):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            if any(secret in str(key).lower() for secret in _SECRET_KEYS):
                redacted[key] = "***"
            else:
                redacted[key] = sanitize_log_data(item)
        return redacted
    if isinstance(value, list):
        return [sanitize_log_data(item) for item in value]
    return value


def configure_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    *,
    stream=None,
) -> None:
    """Send structlog + stdlib logs to console and an optional file."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    console_handler = logging.StreamHandler(stream or sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_pre_chain=shared,
        )
    )

    handlers: list[logging.Handler] = [console_handler]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=shared,
            )
        )
        handlers.append(file_handler)

    root = logging.getLogger()
    root.handlers.clear()
    for handler in handlers:
        root.addHandler(handler)
    root.setLevel(numeric_level)

    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        cache_logger_on_first_use=False,
    )


def configure_mcp_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    """MCP stdio servers must not write to stdout (reserved for protocol framing)."""
    configure_logging(level=level, log_file=log_file, stream=sys.stderr)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def mcp_log_file_from_env() -> Path | None:
    raw = os.environ.get("A2A_LOG_FILE")
    return Path(raw) if raw else None
