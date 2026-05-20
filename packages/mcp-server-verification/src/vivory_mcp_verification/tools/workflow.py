"""Workflow packs — curated verification sequences.

Most agent verification needs decompose into a small number of recurring
sequences: "verify this paper end-to-end", "do due-diligence on this on-
chain protocol", "audit this LLM output's citations". Rather than make
agents stitch 5~10 individual tool calls each time, we expose three
single-call workflow packs that run the sequence server-side and return
one structured report.

Each pack is implemented as a thin orchestrator on the Vivory gateway
that internally hits the same `/verify/*` endpoints individual tools call —
no new data sources, just convenience. The report includes one verdict
per sub-step + an aggregate overall_verdict ∈ {pass, warn, fail}.

- `workflow_paper_repro` — DOI → metadata → retraction → repro hash lookup
  → repro artifact diff. Returns the full verifiability stack of a paper.
- `workflow_crypto_diligence` — chain audit (tx) or contract address +
  admin activity + proxy upgrade history + TVL + entity LEI (if issuer
  provided). For agents writing crypto coverage.
- `workflow_ai_output_verify` — extract citations from arbitrary text →
  resolve each DOI/URL → archive sources → return per-claim pass/fail
  matrix. The default "did this LLM output actually cite real things"
  check.

Backed by /api/verify/workflow/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="workflow_paper_repro",
        description=(
            "End-to-end paper reproducibility verification. Given a DOI, "
            "runs in sequence: doi_metadata → doi_retraction_check → "
            "repro_hub_lookup (Vivory's Reproducibility Hub) → "
            "repro_artifact_diff (if a paper has been reproduced). Returns "
            "a single report with per-step verdict + overall_verdict ∈ "
            "{pass, warn, fail}. `pass` = active DOI + retraction clear + "
            "repro hash matches an artifact; `warn` = active but no repro "
            "yet; `fail` = retracted/withdrawn or repro divergent. Saves "
            "4~5 round trips."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 200,
                    "description": "DOI in any common form.",
                },
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="workflow_crypto_diligence",
        description=(
            "End-to-end crypto-claim due diligence. Given (chain, contract) "
            "+ optional (issuer LEI or protocol slug), runs in sequence: "
            "verify_contract_admin_activity (last 30d) → verify_proxy_"
            "upgrade → verify_protocol_tvl (if protocol slug given) → "
            "verify_lei (if issuer LEI given). Returns a single report "
            "with per-step verdict + overall_verdict + risk flags "
            "(recent_admin_activity, proxy_recently_upgraded, tvl_dropped_"
            "50pct, issuer_lapsed). Use before publishing on-chain claims."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "arbitrum", "base", "optimism", "polygon"],
                },
                "contract": {
                    "type": "string",
                    "pattern": "^0x[0-9a-fA-F]{40}$",
                    "description": "Contract address.",
                },
                "protocol_slug": {
                    "type": "string",
                    "maxLength": 128,
                    "description": "Optional DefiLlama protocol slug for TVL.",
                },
                "issuer_lei": {
                    "type": "string",
                    "pattern": "^[A-Z0-9]{20}$",
                    "description": "Optional 20-char LEI of legal issuer.",
                },
            },
            "required": ["chain", "contract"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="workflow_ai_output_verify",
        description=(
            "End-to-end LLM-output verification. Given a body of generated "
            "text, runs in sequence: extract_citations (DOIs, arXiv IDs, "
            "URLs) → verify_doi (each DOI) → verify_archive (each URL) → "
            "archive_claim_sources (Wayback capture missing). Returns "
            "per-citation pass/fail matrix + overall_verdict ∈ {pass, "
            "warn, fail}. `pass` = all citations resolve, none retracted, "
            "all URLs archived; `warn` = some URLs unarchived; `fail` = "
            "any DOI not-found or retracted, or hallucinated arXiv ID. "
            "The default 'did this LLM actually cite real things' check."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 50_000,
                    "description": "LLM-generated text to verify (markdown OK).",
                },
                "capture_missing_archives": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If True, request Wayback capture for URLs that "
                        "don't yet have a snapshot. Slower (~5s per URL) "
                        "but produces durable archive evidence."
                    ),
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "workflow_paper_repro": lambda a: (
        "POST",
        "verify/workflow/paper-repro",
        None,
        {"doi": a.get("doi")},
    ),
    "workflow_crypto_diligence": lambda a: (
        "POST",
        "verify/workflow/crypto-diligence",
        None,
        {
            "chain": a.get("chain"),
            "contract": a.get("contract"),
            "protocol_slug": a.get("protocol_slug"),
            "issuer_lei": a.get("issuer_lei"),
        },
    ),
    "workflow_ai_output_verify": lambda a: (
        "POST",
        "verify/workflow/ai-output",
        None,
        {
            "text": a.get("text"),
            "capture_missing_archives": a.get("capture_missing_archives", False),
        },
    ),
}
