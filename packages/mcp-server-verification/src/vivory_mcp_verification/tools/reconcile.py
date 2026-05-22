"""Cross-source reconcile tools — company / recall / person verticals.

Three sister tools to the existing `doi_retraction_status` reconcile.
Each calls 2-4 independent registries for the same subject, surfaces
disagreements with severity labels, and returns a deterministic
provenance hash that downstream callers can stamp into verdict
receipts.

Anti-mission #3 (unverified opinion) direct counter: the verdict is
not a Vivory opinion — it's the *consensus or disagreement* of
independent third-party sources. We never claim a single source's
answer is right; we surface how confident the cross-source vote is.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="company_reconcile",
        description=(
            "Cross-source company-entity reconcile — GLEIF + Wikidata "
            "(+ optional NTS Korean biz-validator when `kr_biz_no` is "
            "supplied). Returns per-source legal-name / country / "
            "active-status values, the detected disagreements with "
            "severity labels, a majority-vote reconciled view, and a "
            "deterministic provenance hash. Use this instead of "
            "single-source `verify_lei` / `verify_qid` when the agent "
            "needs a verdict robust to one-registry staleness. Verdict "
            "values: consensus / partial_consensus / disputed / "
            "unverifiable."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Legal entity name.",
                },
                "kr_biz_no": {
                    "type": "string",
                    "maxLength": 20,
                    "description": (
                        "Optional. Korean business number (10 digits, "
                        "with or without hyphens). When supplied, the "
                        "NTS validator is added as a third source."
                    ),
                },
                "include_gleif": {"type": "boolean", "default": True},
                "include_wikidata": {"type": "boolean", "default": True},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="recall_reconcile",
        description=(
            "Cross-jurisdiction recall reconcile — openFDA drug + "
            "openFDA device + CPSC SaferProducts + EU Safety Gate (RAPEX) "
            "for the same product/drug name. Surfaces jurisdiction splits: "
            "recalled in some places but clean in others. Verdict values: "
            "recalled_all / recalled_some (most useful — product is unsafe "
            "somewhere) / clean_all / unverifiable. Each per-source row "
            "carries recall count, most-recent date, highest severity, "
            "and up to 3 sample recall records."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Product or drug name to check.",
                },
                "include_drug": {"type": "boolean", "default": True},
                "include_device": {"type": "boolean", "default": True},
                "include_consumer": {"type": "boolean", "default": True},
                "include_eu": {"type": "boolean", "default": True},
                "limit_per_source": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="person_reconcile",
        description=(
            "Cross-source person-identity reconcile — ORCID public "
            "record + OpenAlex authors + Wikidata. Triangulates display "
            "name + current affiliation + work-count across three "
            "orthogonal registries. Seed with at least one of `orcid`, "
            "`name`, or `qid`. Disagreement is the signal: ORCID "
            "self-curates affiliation (often stale), OpenAlex derives "
            "it bibliometrically (lags by ~6 months), Wikidata "
            "community-curates it. Verdict values: consensus / "
            "partial_consensus / disputed / unverifiable."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "orcid": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "ORCID iD (with or without https://orcid.org/ prefix).",
                },
                "name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 200,
                    "description": "Author display name (used when no orcid/qid given).",
                },
                "qid": {
                    "type": "string",
                    "maxLength": 20,
                    "description": "Wikidata Q-number (with or without Q prefix).",
                },
                "include_orcid": {"type": "boolean", "default": True},
                "include_openalex": {"type": "boolean", "default": True},
                "include_wikidata": {"type": "boolean", "default": True},
            },
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "company_reconcile": lambda a: (
        "GET",
        "verify/company/reconcile",
        {
            "name": a.get("name"),
            "kr_biz_no": a.get("kr_biz_no"),
            "include_gleif": a.get("include_gleif", True),
            "include_wikidata": a.get("include_wikidata", True),
        },
        None,
    ),
    "recall_reconcile": lambda a: (
        "GET",
        "verify/recall/reconcile",
        {
            "query": a.get("query"),
            "include_drug": a.get("include_drug", True),
            "include_device": a.get("include_device", True),
            "include_consumer": a.get("include_consumer", True),
            "include_eu": a.get("include_eu", True),
            "limit_per_source": a.get("limit_per_source", 10),
        },
        None,
    ),
    "person_reconcile": lambda a: (
        "GET",
        "verify/person/reconcile",
        {
            "orcid": a.get("orcid"),
            "name": a.get("name"),
            "qid": a.get("qid"),
            "include_orcid": a.get("include_orcid", True),
            "include_openalex": a.get("include_openalex", True),
            "include_wikidata": a.get("include_wikidata", True),
        },
        None,
    ),
}
