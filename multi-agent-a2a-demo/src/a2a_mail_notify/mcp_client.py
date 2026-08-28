from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from a2a_mail_notify.logging import get_logger, sanitize_log_data

log = get_logger(__name__)


def _text_from_result(result: Any) -> str:
    chunks: list[str] = []
    for block in getattr(result, "content", []) or []:
        if isinstance(block, TextContent):
            chunks.append(block.text)
        elif hasattr(block, "text"):
            chunks.append(str(block.text))
    return "\n".join(chunks)


def tool_result_payload(result: Any) -> Any:
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    text = _text_from_result(result)
    if getattr(result, "is_error", False):
        raise RuntimeError(text or "MCP tool failed")
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


class LoggingMcpClient:
    """MCP client that logs every tool call (args sanitized)."""

    def __init__(self, server_name: str, client: Client) -> None:
        self.server_name = server_name
        self.client = client

    async def list_tools(self) -> list[str]:
        result = await self.client.list_tools()
        names = [tool.name for tool in result.tools]
        log.info("mcp_list_tools", server=self.server_name, tools=names)
        return names

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        arguments = arguments or {}
        started = time.perf_counter()
        log.info(
            "mcp_tool_call_start",
            server=self.server_name,
            tool=name,
            args=sanitize_log_data(arguments),
        )
        try:
            result = await self.client.call_tool(name, arguments)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            log.exception(
                "mcp_tool_call_failed",
                server=self.server_name,
                tool=name,
                duration_ms=duration_ms,
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        is_error = bool(getattr(result, "is_error", False))
        if is_error:
            log.error(
                "mcp_tool_call_error",
                server=self.server_name,
                tool=name,
                duration_ms=duration_ms,
                detail=_text_from_result(result)[:500],
            )
        else:
            log.info(
                "mcp_tool_call_ok",
                server=self.server_name,
                tool=name,
                duration_ms=duration_ms,
            )
        return tool_result_payload(result)


_PASSTHROUGH_ENV = (
    "MAILBOX_HOST",
    "MAILBOX_PORT",
    "MAILBOX_USERNAME",
    "MAILBOX_PASSWORD",
    "MAILBOX_FOLDER",
    "MAILBOX_AUTH",
    "MAILBOX_OAUTH_CLIENT_ID",
    "MAILBOX_OAUTH_TENANT",
    "WHATSAPP_PROVIDER",
    "WHATSAPP_TO",
    "META_WHATSAPP_ACCESS_TOKEN",
    "META_WHATSAPP_PHONE_NUMBER_ID",
    "META_WHATSAPP_API_VERSION",
    "META_WHATSAPP_MESSAGE_MODE",
    "META_WHATSAPP_TEMPLATE_NAME",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_FROM",
    "DRY_RUN",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
)


def _stdio_params(module: str, config_path: Path, log_file: Path, log_level: str) -> StdioServerParameters:
    env = {
        "A2A_CONFIG_PATH": str(config_path.resolve()),
        "A2A_LOG_FILE": str(log_file),
        "A2A_LOG_LEVEL": log_level,
        "PYTHONUNBUFFERED": "1",
    }
    for key in _PASSTHROUGH_ENV:
        value = os.environ.get(key)
        if value:
            env[key] = value
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", module],
        env=env,
        cwd=str(Path.cwd()),
    )


@asynccontextmanager
async def open_email_mcp(config_path: Path, log_file: Path, log_level: str) -> AsyncIterator[LoggingMcpClient]:
    params = _stdio_params("a2a_mail_notify.mcp_servers.email_mcp", config_path, log_file, log_level)
    log.info("mcp_server_spawn", server="email-mcp", module="a2a_mail_notify.mcp_servers.email_mcp")
    async with Client(stdio_client(params)) as client:
        wrapped = LoggingMcpClient("email-mcp", client)
        await wrapped.list_tools()
        yield wrapped


@asynccontextmanager
async def open_whatsapp_mcp(config_path: Path, log_file: Path, log_level: str) -> AsyncIterator[LoggingMcpClient]:
    params = _stdio_params(
        "a2a_mail_notify.mcp_servers.whatsapp_mcp", config_path, log_file, log_level
    )
    log.info("mcp_server_spawn", server="whatsapp-mcp", module="a2a_mail_notify.mcp_servers.whatsapp_mcp")
    async with Client(stdio_client(params)) as client:
        wrapped = LoggingMcpClient("whatsapp-mcp", client)
        await wrapped.list_tools()
        yield wrapped
