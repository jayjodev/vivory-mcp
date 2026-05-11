"""Vivory Verification umbrella MCP server.

Aggregates verifiable-AI-work tools under a single MCP server name
(`vivory-verification`). Ships 27 tools across 9 categories:

- claim       (3) — verify_claim, extract_citations, archive_claim_sources
- doi         (4) — verify_doi, doi_metadata, doi_retraction_check, doi_author_network
- archive     (3) — verify_archive, wayback_capture, wayback_history
- repro       (3) — verify_repro_hash, repro_hub_lookup, repro_artifact_diff
- provenance  (4) — verify_c2pa, verify_pdf_provenance, verify_hash_chain, detect_watermark
- peer-review (2) — verify_peer_review, persona_verdict_lookup
- forecast    (2) — forecast_track_record (crypto.vivory.app/forecast), submit_forecast
- filing      (3) — verify_filing, filing_recent, filing_facts (SEC EDGAR — sister of Korea DART)
- entity      (3) — verify_lei, entity_search, entity_relationships (GLEIF LEI)

Architecture:
- Tool definitions live in `tools/{category}.py` per concern
- `server.py` aggregates them into a single MCP catalog
- Each handler returns (method, path, params, body); `client.request` dispatches
  to api.vivory.app/api/{path}
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
    archive as archive_tools,
    claim as claim_tools,
    doi as doi_tools,
    entity as entity_tools,
    filing as filing_tools,
    forecast as forecast_tools,
    peer_review as peer_review_tools,
    provenance as provenance_tools,
    repro as repro_tools,
)

logger = logging.getLogger("vivory_mcp_verification")

server: Server = Server("vivory-verification")


TOOLS: list[Tool] = [
    *claim_tools.TOOLS,
    *doi_tools.TOOLS,
    *archive_tools.TOOLS,
    *repro_tools.TOOLS,
    *provenance_tools.TOOLS,
    *peer_review_tools.TOOLS,
    *forecast_tools.TOOLS,
    *filing_tools.TOOLS,
    *entity_tools.TOOLS,
]


HANDLERS: dict[str, Any] = {
    **claim_tools.HANDLERS,
    **doi_tools.HANDLERS,
    **archive_tools.HANDLERS,
    **repro_tools.HANDLERS,
    **provenance_tools.HANDLERS,
    **peer_review_tools.HANDLERS,
    **forecast_tools.HANDLERS,
    **filing_tools.HANDLERS,
    **entity_tools.HANDLERS,
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
        method, path, params, body = handler(args)
        data = await client.request(method, path, params=params, json_body=body)
    except Exception as exc:
        logger.exception("tool %s failed", name)
        return [TextContent(
            type="text",
            text=f"Vivory Verification Gateway error ({type(exc).__name__}): {exc}",
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
