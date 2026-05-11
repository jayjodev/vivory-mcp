"""Reproducibility hash registry tools — Vivory Repro Hub.

Vivory's Reproducibility Hub publishes hand-crafted notebook reproductions
of recent ML papers, each with a content-addressed hash chain (notebook +
weights + outputs). These tools let an AI agent ask: "is this paper's
reproduction in the registry?" or "do these two reproduction artifacts
match?" — with a deterministic verifiable answer rather than a literature
search.

Backed by /api/research/repro/* + /api/verify/repro/* on api.vivory.app.
The Repro Hub itself is at https://research.vivory.app/repro.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_HASH = {
    "type": "string",
    "pattern": "^[a-fA-F0-9]{16,128}$",
    "description": "Content hash (sha256 / blake3) — hex, 16-128 chars.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_repro_hash",
        description=(
            "Check whether a content hash matches a published Vivory Repro "
            "Hub artifact. Returns the matching reproduction's paper title, "
            "DOI, arXiv ID, reproduction verdict (full / partial / failed / "
            "intentionally-out-of-scope), and the receipt URL. Use this when "
            "an LLM claims to have run a specific known notebook — agents "
            "can verify the artifact bytes match a registered reproduction."
        ),
        inputSchema={
            "type": "object",
            "properties": {"hash": _HASH},
            "required": ["hash"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="repro_hub_lookup",
        description=(
            "Search the Repro Hub by paper title, DOI, arXiv ID, or year. "
            "Returns matching reproductions with verdict, hardware used "
            "(P100 / A100 / T4 / etc.), reproduction date, and the published "
            "notebook URL. For LLMs deciding whether to claim a paper has "
            "been independently reproduced — answer is verifiable by hash."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "paper_title": {"type": "string", "minLength": 2, "maxLength": 300},
                "doi": {"type": "string", "minLength": 4, "maxLength": 200},
                "arxiv_id": {
                    "type": "string",
                    "pattern": "^\\d{4}\\.\\d{4,5}(v\\d+)?$|^[a-z\\-]+/\\d{7}$",
                },
                "year": {"type": "integer", "minimum": 2010, "maximum": 2030},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="repro_artifact_diff",
        description=(
            "Compare two reproduction artifacts by hash. Returns whether "
            "they match exactly (same hash), are sibling reproductions of "
            "the same paper (different hardware / seed), or are unrelated. "
            "When sibling, surfaces the metric delta (e.g. 'FID-50K diff "
            "0.04, within reproduction tolerance')."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "hash_a": _HASH,
                "hash_b": _HASH,
            },
            "required": ["hash_a", "hash_b"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_repro_hash": lambda a: ("GET", "verify/repro/by-hash", {"hash": a.get("hash")}, None),
    "repro_hub_lookup": lambda a: (
        "GET",
        "verify/repro/lookup",
        {
            "paper_title": a.get("paper_title"),
            "doi": a.get("doi"),
            "arxiv_id": a.get("arxiv_id"),
            "year": a.get("year"),
            "limit": a.get("limit"),
        },
        None,
    ),
    "repro_artifact_diff": lambda a: (
        "GET",
        "verify/repro/diff",
        {"hash_a": a.get("hash_a"), "hash_b": a.get("hash_b")},
        None,
    ),
}
