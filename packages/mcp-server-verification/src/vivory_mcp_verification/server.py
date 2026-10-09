"""End-of-service MCP server.

Exposes one tool, `service_status`, so an agent that still has this server
configured gets a clear answer instead of an HTTP error from a redirect.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import __version__

NOTICE = (
    "vivory-mcp-verification has been discontinued. The hosted API it called "
    "(api.vivory.app) was shut down on 2026-08-09, so the verification tools from "
    "versions up to 0.14.0 no longer work. There is no paid plan and no new keys "
    "are issued. Please remove this server from your MCP client configuration. "
    "Contact: contact@vivory.app"
)

STATUS_TOOL = Tool(
    name="service_status",
    description=(
        "Explains that the Vivory verification service has been discontinued. "
        "Call it to read the notice. Takes no arguments."
    ),
    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
)

server: Server = Server("vivory-verification")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [STATUS_TOOL]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    if name == STATUS_TOOL.name:
        return [TextContent(type="text", text=NOTICE)]
    # A config or prompt written for 0.14.0 may still name an old tool.
    raise ValueError(f"'{name}' is not available. {NOTICE}")


async def run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in ("--help", "-h", "--version"):
        print(f"vivory-mcp-verification {__version__}\n\n{NOTICE}")
        return
    print(f"[vivory-mcp-verification {__version__}] {NOTICE}", file=sys.stderr, flush=True)
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
