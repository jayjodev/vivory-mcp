"""Vivory Korea umbrella MCP server.

Aggregates all Korean public-data tools under a single MCP server
(`vivory-korea`). v0.1 ships KOSIS only (15 tools); future versions
add ECOS, NEIS, LOCALDATA, etc. without changing the registration
command — users install once and get new tools automatically as
this package grows.

Architecture:
- Tool definitions live in `tools/{source}.py` per data source
- `server.py` aggregates them into a single MCP catalog
- HTTP routing: tool name prefix decides path
  (e.g. kosis_* → /public-tools/kosis/*, ecos_* → /public-tools/bok/*)
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import client
from .tools import kosis as kosis_tools

logger = logging.getLogger("vivory_mcp_korea")

server: Server = Server("vivory-korea")


# Aggregate tool catalog from all sources
TOOLS: list[Tool] = [
    *kosis_tools.TOOLS,
    # Future: *ecos_tools.TOOLS, *neis_tools.TOOLS, *localdata_tools.TOOLS, ...
]

# Aggregate handlers from all sources
HANDLERS: dict[str, Any] = {
    **kosis_tools.HANDLERS,
    # Future merges from other sources
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    handler = HANDLERS.get(name)
    if handler is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        path, params = handler(args)
        data = await client.get(path, params)
    except Exception as exc:
        logger.exception("tool %s failed", name)
        return [TextContent(
            type="text",
            text=f"Vivory Korea Data Gateway error ({type(exc).__name__}): {exc}",
        )]

    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
