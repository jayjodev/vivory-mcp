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
from .tools import (
    air_quality as air_quality_tools,
    bok as bok_tools,
    dart as dart_tools,
    healthcare as healthcare_tools,
    kosis as kosis_tools,
    misc as misc_tools,
    mobility as mobility_tools,
    opinet as opinet_tools,
    real_estate as real_estate_tools,
    tour as tour_tools,
    vworld as vworld_tools,
    weather as weather_tools,
)

logger = logging.getLogger("vivory_mcp_korea")

server: Server = Server("vivory-korea")


# Aggregate tool catalog from all sources
TOOLS: list[Tool] = [
    *kosis_tools.TOOLS,
    *bok_tools.TOOLS,
    *dart_tools.TOOLS,
    *weather_tools.TOOLS,
    *air_quality_tools.TOOLS,
    *opinet_tools.TOOLS,
    *healthcare_tools.TOOLS,
    *real_estate_tools.TOOLS,
    *tour_tools.TOOLS,
    *mobility_tools.TOOLS,
    *vworld_tools.TOOLS,
    *misc_tools.TOOLS,
]

# Aggregate handlers from all sources
HANDLERS: dict[str, Any] = {
    **kosis_tools.HANDLERS,
    **bok_tools.HANDLERS,
    **dart_tools.HANDLERS,
    **weather_tools.HANDLERS,
    **air_quality_tools.HANDLERS,
    **opinet_tools.HANDLERS,
    **healthcare_tools.HANDLERS,
    **real_estate_tools.HANDLERS,
    **tour_tools.HANDLERS,
    **mobility_tools.HANDLERS,
    **vworld_tools.HANDLERS,
    **misc_tools.HANDLERS,
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


def _startup_banner() -> None:
    """Print tier + tool-count banner to stderr.

    Anonymous users see the upgrade path *before* hitting a 429. Pro users
    see confirmation that their key is being sent. Both surface the
    sibling Verification MCP because one $29/mo key unlocks both.
    """
    has_key = client.get_api_key() is not None
    base = client.get_api_base()
    tool_count = len(TOOLS)
    if has_key:
        print(
            f"[vivory-mcp-korea] {tool_count} tools across 15 sources | Pro tier (Bearer key sent) | "
            f"gateway={base} | sibling: `uvx vivory-mcp-verification` (same key unlocks 45 verification tools)",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"[vivory-mcp-korea] {tool_count} tools across 15 sources | Anonymous tier (100/day per IP) | "
            f"gateway={base}\n"
            f"  → Upgrade to Pro 10k/day ($29/mo USDC, no auto-renew, no custody) at\n"
            f"    https://api.vivory.app/dashboard/public-api — same key unlocks the\n"
            f"    sibling `vivory-mcp-verification` (45 tools), 100+ tools total.",
            file=sys.stderr,
            flush=True,
        )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    _startup_banner()
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
