"""MCP client wrapper that logs every tool call an agent makes.

Each agent spawns its MCP server over stdio and talks to it through
`LoggedMcpClient`, so the log file shows the full chain:
agent -> MCP tool -> provider -> result.
"""

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

from mail_a2a.config import PASSTHROUGH_ENV, config_path
from mail_a2a.logging_setup import get_logger, redact

log = get_logger(__name__)

EMAIL_SERVER_MODULE = "mail_a2a.mcp_servers.email_mcp"
WHATSAPP_SERVER_MODULE = "mail_a2a.mcp_servers.whatsapp_mcp"


def _result_text(result: Any) -> str:
    chunks = [
        block.text
        for block in (getattr(result, "content", None) or [])
        if getattr(block, "text", None)
    ]
    return "\n".join(chunks)


def _result_payload(result: Any) -> Any:
    """Prefer the structured output; fall back to parsing the text content."""
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    text = _result_text(result)
    if getattr(result, "is_error", False):
        raise RuntimeError(text or "MCP tool returned an error")
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


class LoggedMcpClient:
    """Wraps an MCP session and records each call with timing and outcome."""

    def __init__(self, server_name: str, client: Client) -> None:
        self.server_name = server_name
        self._client = client

    async def list_tools(self) -> list[str]:
        result = await self._client.list_tools()
        names = [tool.name for tool in result.tools]
        log.info("mcp_tools_discovered", server=self.server_name, tools=names)
        return names

    async def call(self, tool: str, arguments: dict[str, Any] | None = None) -> Any:
        arguments = arguments or {}
        started = time.perf_counter()
        log.info(
            "mcp_call_start",
            server=self.server_name,
            tool=tool,
            args=redact(arguments),
        )
        try:
            result = await self._client.call_tool(tool, arguments)
        except Exception as exc:
            log.error(
                "mcp_call_failed",
                server=self.server_name,
                tool=tool,
                duration_ms=round((time.perf_counter() - started) * 1000, 1),
                error=str(exc),
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        if getattr(result, "is_error", False):
            log.error(
                "mcp_call_error",
                server=self.server_name,
                tool=tool,
                duration_ms=duration_ms,
                detail=_result_text(result)[:500],
            )
        else:
            log.info("mcp_call_ok", server=self.server_name, tool=tool, duration_ms=duration_ms)
        return _result_payload(result)


def _stdio_params(module: str) -> StdioServerParameters:
    """Launch the MCP server with the same interpreter, config and log target."""
    env = {
        "MAIL_A2A_CONFIG": str(config_path().resolve()),
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }
    for key in PASSTHROUGH_ENV:
        if value := os.environ.get(key):
            env[key] = value
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", module],
        env={k: v for k, v in env.items() if v},
        cwd=str(Path.cwd()),
    )


@asynccontextmanager
async def open_mcp(server_name: str, module: str) -> AsyncIterator[LoggedMcpClient]:
    log.info("mcp_server_spawn", server=server_name, module=module)
    async with Client(stdio_client(_stdio_params(module))) as client:
        wrapped = LoggedMcpClient(server_name, client)
        await wrapped.list_tools()
        try:
            yield wrapped
        finally:
            log.info("mcp_server_closing", server=server_name)


def open_email_mcp() -> Any:
    return open_mcp("email-mcp", EMAIL_SERVER_MODULE)


def open_whatsapp_mcp() -> Any:
    return open_mcp("whatsapp-mcp", WHATSAPP_SERVER_MODULE)
