"""Press-release-vs-article fidelity diff.

A journalism-side verification primitive: how much of a published article
is just the press release, repackaged? High-fidelity copy-paste is one of
the strongest signals of PR-driven content (anti-mission #4 — AI/PR slop).

v0.1 approach: deterministic n-gram overlap + sentence-level alignment.
Returns:
- overall_overlap_ratio (% of article tokens that appear in PR)
- longest_shared_span (longest contiguous shared phrase)
- sentence_alignment (per-sentence: original / paraphrased / verbatim)
- verdict (pr_dominant / pr_heavy / mixed / independent)

No LLM call required at v0.1 — cheap + deterministic + reproducible.
v0.2 will optionally LLM-rank paraphrased sentences.

Backed by /api/verify/pr-article/diff.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_pr_article_diff",
        description=(
            "Diff a published news article against a press-release source "
            "(or two text bodies) to measure how much was copy-pasted vs. "
            "independently reported. Returns overall overlap ratio, longest "
            "shared phrase, per-sentence alignment (verbatim / paraphrased / "
            "original), and a verdict on a four-tier scale (independent / "
            "mixed / pr_heavy / pr_dominant). Use to spot churnalism + "
            "PR-driven publishing. Cheap + deterministic — no LLM cost at v0.1."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "article_text": {
                    "type": "string",
                    "minLength": 50,
                    "maxLength": 200_000,
                    "description": "Full text of the article being checked.",
                },
                "pr_text": {
                    "type": "string",
                    "minLength": 50,
                    "maxLength": 200_000,
                    "description": (
                        "Full text of the press release (or any baseline text "
                        "to diff against)."
                    ),
                },
                "min_ngram": {
                    "type": "integer",
                    "minimum": 3,
                    "maximum": 20,
                    "default": 6,
                    "description": (
                        "Minimum shared n-gram length (in tokens) to count "
                        "as a 'verbatim' span. 6 = ~one short sentence chunk."
                    ),
                },
            },
            "required": ["article_text", "pr_text"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_pr_article_diff": lambda a: (
        "POST",
        "verify/pr-article/diff",
        None,
        {
            "article_text": a.get("article_text"),
            "pr_text": a.get("pr_text"),
            "min_ngram": a.get("min_ngram") or 6,
        },
    ),
}
