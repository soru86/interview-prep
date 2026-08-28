"""Structured logging shared by the agents, the MCP servers and the runner.

Console gets a human-readable rendering, the log file gets one JSON object per
line so the whole multi-process run can be replayed with `jq`.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, TextIO

import structlog

# Substrings that mark a config/tool argument as secret.
_SECRET_HINTS = ("password", "token", "secret", "auth_token", "authorization", "sid", "api_key")


def redact(value: Any) -> Any:
    """Recursively replace secret-looking values so they never reach a log sink."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(hint in str(key).lower() for hint in _SECRET_HINTS):
                out[key] = "***" if item else ""
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value


def configure_logging(
    level: str = "INFO",
    log_file: Path | str | None = None,
    *,
    stream: TextIO | None = None,
) -> None:
    """Wire structlog + stdlib logging to the console and (optionally) a file."""
    numeric_level = getattr(logging, str(level).upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    console_handler = logging.StreamHandler(stream or sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
            foreign_pre_chain=shared_processors,
        )
    )
    handlers: list[logging.Handler] = [console_handler]

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=shared_processors,
            )
        )
        handlers.append(file_handler)

    root = logging.getLogger()
    root.handlers.clear()
    for handler in handlers:
        root.addHandler(handler)
    root.setLevel(numeric_level)

    # uvicorn installs its own handlers; force it through ours instead.
    for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access", "httpx", "httpcore"):
        logger = logging.getLogger(noisy)
        logger.handlers.clear()
        logger.propagate = True
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # The SDK dumps the whole agent card at INFO; we log a2a_peer_resolved instead.
    logging.getLogger("a2a.client.card_resolver").setLevel(logging.WARNING)

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        cache_logger_on_first_use=False,
    )


def configure_stdio_server_logging(level: str = "INFO", log_file: Path | str | None = None) -> None:
    """Logging for MCP stdio servers.

    stdout carries the MCP protocol framing, so anything we print there would
    corrupt the session. Console logs go to stderr instead.
    """
    configure_logging(level=level, log_file=log_file, stream=sys.stderr)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def log_file_from_env() -> str | None:
    """MCP servers are spawned as subprocesses and inherit the log target here."""
    return os.environ.get("MAIL_A2A_LOG_FILE") or None
