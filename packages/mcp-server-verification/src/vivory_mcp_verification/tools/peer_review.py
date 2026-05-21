"""Peer review verdict lookup — Vivory Universal Peer Review pipeline.

Every article published through Vivory (Life · Crypto · Research) runs
through `universal_peer_review` — a 2-to-3-persona panel that scores
content on domain accuracy / clarity / safety dimensions and votes
accept / revise / reject. These tools let an outside agent fetch the
verdict envelope so they can decide whether to cite a Vivory article as
authoritative.

Backed by `/api/verify/peer-review/*` on api.vivory.app. Read-only —
submission is internal to Vivory's pipeline (Phase B candidate, gated
on anti-mission #4 review per project_peer_review_mcp_planning_2026_05_16).
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
            "Fetch the peer-review verdict envelope for a Vivory article. "
            "Returns reviewers (persona panel), per-persona verdict "
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
    Tool(
        name="bulk_peer_review_lookup",
        description=(
            "Lookup peer-review verdicts for up to 100 Vivory article IDs "
            "in a single call. Returns a per-id results array plus a "
            "summary count (found / not_found / no_review / invalid). "
            "Use this when verifying a citation list — one round trip "
            "instead of N. Each result has the same shape as "
            "verify_peer_review's envelope."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "article_ids": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 100,
                    "items": {"type": "string", "minLength": 1, "maxLength": 200},
                    "description": (
                        "1-100 Vivory article identifiers (numeric IDs or "
                        "slugs). Mixed services OK — the gateway resolves "
                        "each across research / crypto / life."
                    ),
                },
            },
            "required": ["article_ids"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="reviewer_registry",
        description=(
            "Public registry of the persona panels Vivory peer review "
            "uses. Returns per-service: persona name, scoring model "
            "(claude-opus-4-7 / claude-sonnet-4-6), and the score "
            "dimensions each persona evaluates (e.g. Life Domain scores "
            "domain accuracy / executability / specificity / safety). "
            "Also returns the verdict aggregation rule so callers can "
            "reproduce the math from raw scores. Persona prompts are "
            "intentionally not exposed — Trust transparency vs. gate "
            "moat split per planning doc decision 4."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="peer_review_stats",
        description=(
            "Aggregate peer-review verdict distribution across Vivory "
            "services. Returns per-service: count of reviewed articles, "
            "verdict distribution (accept / revise / reject / other), "
            "and average overall score. Optional `service` filter "
            "narrows to one of life / crypto / research. Useful for "
            "verifying a publisher's track record — e.g. 'what fraction "
            "of Vivory Life recipes pass peer review?'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "enum": ["life", "crypto", "research"],
                    "description": "Optional — narrow to one service. Omit for all.",
                },
            },
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
    "bulk_peer_review_lookup": lambda a: (
        "POST",
        "verify/peer-review/bulk",
        None,
        {"article_ids": a.get("article_ids") or []},
    ),
    "reviewer_registry": lambda a: (
        "GET",
        "verify/peer-review/reviewers",
        None,
        None,
    ),
    "peer_review_stats": lambda a: (
        "GET",
        "verify/peer-review/stats",
        {"service": a.get("service")},
        None,
    ),
}
