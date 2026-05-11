"""Peer review verdict lookup — Vivory Research peer-review pipeline.

Vivory Research runs every published article through a multi-persona peer
review (reviewer panel + verdict aggregation). These tools let an AI agent
fetch the verdict envelope: was this article peer-reviewed? what did the
reviewers say? did any persona reject?

Backed by /api/verify/peer-review/* + /api/research/peer-review/* on
api.vivory.app. Read-only — submission is internal to Vivory's pipeline.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_ARTICLE_ID = {
    "type": "string",
    "minLength": 1,
    "maxLength": 200,
    "description": (
        "Vivory article identifier — numeric ID (e.g. '1251'), slug "
        "(e.g. 'aria-shen-gca-bulf'), or full URL. The gateway normalizes."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_peer_review",
        description=(
            "Fetch the peer-review verdict envelope for a Vivory Research "
            "article. Returns reviewers (persona panel), per-persona verdict "
            "(accept / minor-revise / major-revise / reject), aggregate "
            "verdict, review date, and any heuristic gate triggers (e.g. "
            "MSE-inequality soft-revise, truncation hard-reject, Popper "
            "term soft-revise). Use this before citing a Vivory article "
            "as supporting evidence — articles with verdict='reject' or "
            "missing peer review should not be treated as authoritative."
        ),
        inputSchema={
            "type": "object",
            "properties": {"article_id": _ARTICLE_ID},
            "required": ["article_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="persona_verdict_lookup",
        description=(
            "Get a single reviewer persona's verdict on a Vivory article. "
            "Useful when an LLM has cited a specific persona's analysis "
            "and needs to confirm the verdict was actually that persona's "
            "(not aggregated). Returns the persona's verdict, written "
            "feedback excerpt, confidence, and any concern flags."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "article_id": _ARTICLE_ID,
                "persona": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "Persona identifier (slug or display name).",
                },
            },
            "required": ["article_id", "persona"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_peer_review": lambda a: (
        "GET",
        "verify/peer-review/by-article",
        {"article_id": a.get("article_id")},
        None,
    ),
    "persona_verdict_lookup": lambda a: (
        "GET",
        "verify/peer-review/persona",
        {"article_id": a.get("article_id"), "persona": a.get("persona")},
        None,
    ),
}
