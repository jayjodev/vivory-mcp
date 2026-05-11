"""Claim verification tools — extract / verify / archive citations from arbitrary text.

The flagship category. An AI agent that has just generated a paragraph of
prose can call ``verify_claim`` to get back a structured assessment of every
checkable assertion: which claims have citations, which citations resolve,
which still need archival snapshots, which look like fabrications. The
``extract_citations`` tool is a cheaper subset for when the agent only needs
the citation list (no source-by-source verdict). ``archive_claim_sources``
takes a list of citations and submits the cited URLs to Wayback in one batch.

Backed by /api/verify/claim/* on api.vivory.app. Combines Vivory's own
citation-trail service with upstream Crossref / OpenAlex / Wayback.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_claim",
        description=(
            "Run Vivory's full claim-verification pipeline on an arbitrary "
            "block of text. Extracts each checkable assertion, attempts to "
            "resolve any inline citations (DOI / arXiv / URL / Wayback), "
            "checks each cited source's reachability + archival coverage, "
            "and returns a per-claim verdict (verified / partial / unverified "
            "/ likely-fabricated). Mode 'fast' (default) caps at 20 claims "
            "and skips deep retraction lookup; 'thorough' walks every claim "
            "through retraction + author-network checks (slower, costs more "
            "rate-limit budget)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 50000,
                    "description": "The prose to verify. UTF-8, plain text or markdown.",
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "description": (
                        "Optional pre-supplied source URLs. If the LLM already "
                        "knows what it's citing, pass the URLs explicitly to "
                        "skip extraction and go straight to verification."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["fast", "thorough"],
                    "default": "fast",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="extract_citations",
        description=(
            "Pull the citation list out of arbitrary text without running "
            "verification. Returns DOIs / arXiv IDs / URLs / Wayback links "
            "found in the text, plus a citation_kind tag (formal / inline / "
            "narrative / footnote). Cheap — no upstream lookups. Use this "
            "when the LLM just needs the bibliography to format or render."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 50000,
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="archive_claim_sources",
        description=(
            "Submit a list of source URLs to Wayback Machine in batch and "
            "return the resulting snapshot URLs. For agents that need to "
            "lock in archival evidence before a citation rots. Idempotent "
            "— re-submission within 1h returns cached snapshot rather than "
            "re-capturing. Max 50 URLs per call."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "citations": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "maxItems": 50,
                    "description": "URLs to snapshot.",
                },
                "include_history": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, also return existing Wayback snapshots for each URL.",
                },
            },
            "required": ["citations"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_claim": lambda a: (
        "POST",
        "verify/claim",
        None,
        {
            "text": a.get("text"),
            "sources": a.get("sources"),
            "mode": a.get("mode") or "fast",
        },
    ),
    "extract_citations": lambda a: (
        "POST",
        "verify/claim/extract-citations",
        None,
        {"text": a.get("text")},
    ),
    "archive_claim_sources": lambda a: (
        "POST",
        "verify/claim/archive-sources",
        None,
        {
            "citations": a.get("citations") or [],
            "include_history": bool(a.get("include_history")),
        },
    ),
}
