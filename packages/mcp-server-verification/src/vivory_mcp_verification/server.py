"""Vivory Verification umbrella MCP server.

Aggregates verifiable-AI-work tools under a single MCP server name
(`vivory-verification`). v0.9 ships 89 tools across 36 categories:

- claim       (3) — verify_claim, extract_citations, archive_claim_sources
- doi         (4) — verify_doi, doi_metadata, doi_retraction_check, doi_author_network
- archive     (3) — verify_archive, wayback_capture, wayback_history
- repro       (3) — verify_repro_hash, repro_hub_lookup, repro_artifact_diff
- provenance  (4) — verify_c2pa, verify_pdf_provenance, verify_hash_chain, detect_watermark
- peer-review (5) — verify_peer_review, persona_verdict_lookup, bulk_peer_review_lookup, reviewer_registry, peer_review_stats (Universal Peer Review trail — panel registry + bulk lookup + service-level stats)
- forecast    (4) — forecast_track_record (crypto.vivory.app/forecast), submit_forecast, forecast_ensemble (Polymarket+Kalshi+Manifold consensus), forecast_calibration (ECE/MCE/Brier)
- filing      (3) — verify_filing, filing_recent, filing_facts (SEC EDGAR — sister of Korea DART)
- entity      (3) — verify_lei, entity_search, entity_relationships (GLEIF LEI)
- work        (3) — verify_work, search_works, verify_salami_slicing (OpenAlex academic citation graph + author near-dup screen)
- wikidata    (2) — verify_qid, wikidata_search (entity grounding via Q-numbers)
- trial       (2) — verify_trial, trial_search (ClinicalTrials.gov v2)
- indicator   (2) — verify_indicator, indicator_series (World Bank Open Data)
- patent      (2) — verify_patent, patent_search (USPTO PatentsView)
- place       (2) — verify_place, place_search (OpenStreetMap Nominatim)
- tvl         (2) — verify_protocol_tvl, verify_chain_tvl (DefiLlama crypto TVL)
- quake       (2) — verify_quake, recent_quakes (USGS Earthquake)
- apt         (2) — apt_market_snapshot, verify_apt_price (MOLIT RTMS — Korean apartment real-transaction prices, daily nationwide ingest)
- identity    (2) — verify_orcid, orcid_works (ORCID public API)
- web         (2) — verify_url_hash, verify_dataset_fingerprint (content-trail + structure probe)
- domain      (4) — verify_domain_whois, verify_domain_dns, verify_domain_owner_change, verify_domain_history (RDAP + Cloudflare DoH + WHOIS history poll)
- chain       (4) — blockchain_audit_lookup, blockchain_audit_chains, verify_contract_admin_activity, verify_proxy_upgrade (EVM signed audit + contract pollers)
- npm         (2) — verify_npm_package, verify_npm_typosquat (registry.npmjs.org supply chain)
- pypi        (2) — verify_pypi_package, verify_pypi_typosquat (pypi.org supply chain)
- retraction  (3) — doi_retraction_status, retraction_watch_recent, retraction_watch_by_journal (Retraction Watch + Crossref crossmark)
- workflow    (3) — workflow_paper_repro, workflow_crypto_diligence, workflow_ai_output_verify (curated multi-step verification)
- policy      (2) — policy_list_presets, policy_evaluate (custom verification policy framework)
- law         (5) — kor_law_lookup, kor_law_currency, kor_case_search, kor_bill_status, kor_company_status (국가법령정보센터 + 열린국회정보 + NTS×CSL Verified Fact corpus first two verticals)
- sanctions   (1) — sanctions_screen (OFAC + UN + EU + KR STIC via openSanctions)
- recall      (2) — drug_recall_check, product_recall_check (openFDA + CPSC SaferProducts)
- journal     (1) — verify_journal_quality (DOAJ whitelist + predatory heuristic)
- pr_diff     (1) — verify_pr_article_diff (press-release vs article fidelity diff)
- pubpeer     (1) — verify_pubpeer_status (PubPeer post-publication peer-review commentary)
- opencitations (1) — verify_doi_citations (OpenCitations COCI citation context + self-citation count)
- funder      (1) — verify_funder (Crossref Funder Registry resolver)
- wikipedia   (1) — verify_wikipedia_cite_health (Wikipedia external-link liveness audit)

Architecture:
- Tool definitions live in `tools/{category}.py` per concern
- `server.py` aggregates them into a single MCP catalog
- Each handler returns (method, path, params, body); `client.request` dispatches
  to api.vivory.app/api/{path}
"""
from __future__ import annotations

import asyncio
import difflib
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import client
from .tools import (
    apt as apt_tools,
    archive as archive_tools,
    chain as chain_tools,
    claim as claim_tools,
    doi as doi_tools,
    domain as domain_tools,
    entity as entity_tools,
    filing as filing_tools,
    forecast as forecast_tools,
    identity as identity_tools,
    indicator as indicator_tools,
    journal as journal_tools,
    law as law_tools,
    npm as npm_tools,
    opencitations as opencitations_tools,
    patent as patent_tools,
    peer_review as peer_review_tools,
    place as place_tools,
    policy as policy_tools,
    pr_diff as pr_diff_tools,
    provenance as provenance_tools,
    pubpeer as pubpeer_tools,
    pypi as pypi_tools,
    quake as quake_tools,
    recall as recall_tools,
    repro as repro_tools,
    retraction as retraction_tools,
    sanctions as sanctions_tools,
    trial as trial_tools,
    tvl as tvl_tools,
    web as web_tools,
    wikidata as wikidata_tools,
    wikipedia as wikipedia_tools,
    work as work_tools,
    workflow as workflow_tools,
    funder as funder_tools,
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
    *work_tools.TOOLS,
    *wikidata_tools.TOOLS,
    *trial_tools.TOOLS,
    *indicator_tools.TOOLS,
    *patent_tools.TOOLS,
    *place_tools.TOOLS,
    *tvl_tools.TOOLS,
    *quake_tools.TOOLS,
    *apt_tools.TOOLS,
    *identity_tools.TOOLS,
    *web_tools.TOOLS,
    *domain_tools.TOOLS,
    *chain_tools.TOOLS,
    *npm_tools.TOOLS,
    *pypi_tools.TOOLS,
    *retraction_tools.TOOLS,
    *workflow_tools.TOOLS,
    *policy_tools.TOOLS,
    *law_tools.TOOLS,
    *sanctions_tools.TOOLS,
    *recall_tools.TOOLS,
    *journal_tools.TOOLS,
    *pr_diff_tools.TOOLS,
    *pubpeer_tools.TOOLS,
    *opencitations_tools.TOOLS,
    *funder_tools.TOOLS,
    *wikipedia_tools.TOOLS,
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
    **work_tools.HANDLERS,
    **wikidata_tools.HANDLERS,
    **trial_tools.HANDLERS,
    **indicator_tools.HANDLERS,
    **patent_tools.HANDLERS,
    **place_tools.HANDLERS,
    **tvl_tools.HANDLERS,
    **quake_tools.HANDLERS,
    **apt_tools.HANDLERS,
    **identity_tools.HANDLERS,
    **web_tools.HANDLERS,
    **domain_tools.HANDLERS,
    **chain_tools.HANDLERS,
    **npm_tools.HANDLERS,
    **pypi_tools.HANDLERS,
    **retraction_tools.HANDLERS,
    **workflow_tools.HANDLERS,
    **policy_tools.HANDLERS,
    **law_tools.HANDLERS,
    **sanctions_tools.HANDLERS,
    **recall_tools.HANDLERS,
    **journal_tools.HANDLERS,
    **pr_diff_tools.HANDLERS,
    **pubpeer_tools.HANDLERS,
    **opencitations_tools.HANDLERS,
    **funder_tools.HANDLERS,
    **wikipedia_tools.HANDLERS,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


def _classify_error(exc: BaseException) -> str:
    """Map exception → stable error code for agents to branch on."""
    msg = str(exc).lower()
    if "rate limit" in msg or "429" in msg:
        return "RATE_LIMIT"
    if "rejected" in msg or "401" in msg or "auth" in msg:
        return "AUTH"
    if "timeout" in msg or "timed out" in msg or isinstance(exc, TimeoutError):
        return "TIMEOUT"
    if "404" in msg or "not found" in msg:
        return "NOT_FOUND"
    if isinstance(exc, ValueError):
        return "VALIDATION"
    return "UPSTREAM"


def _error_envelope(tool: str, exc: BaseException) -> dict[str, Any]:
    return {
        "error": f"{type(exc).__name__}: {exc}",
        "code": _classify_error(exc),
        "tool": tool,
        "gateway": "vivory-mcp-verification",
    }


def _did_you_mean(name: str, registry: dict[str, Any], k: int = 3) -> list[str]:
    """Fuzzy-match an unknown tool name against the registered catalog.

    Uses difflib.get_close_matches with a permissive cutoff so agents that
    mistype `verify_doi_metadata` → `doi_metadata` (or vice versa) get a
    useful hint instead of just `UNKNOWN_TOOL`. Returns up to k candidates,
    most-similar first.
    """
    if not name:
        return []
    return difflib.get_close_matches(name, list(registry.keys()), n=k, cutoff=0.55)


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    handler = HANDLERS.get(name)
    if handler is None:
        suggestions = _did_you_mean(name, HANDLERS)
        envelope = {
            "error": f"Unknown tool: {name}",
            "code": "UNKNOWN_TOOL",
            "tool": name,
            "gateway": "vivory-mcp-verification",
            "did_you_mean": suggestions,
        }
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    try:
        method, path, params, body = handler(args)
        data = await client.request(method, path, params=params, json_body=body)
    except Exception as exc:
        logger.exception("tool %s failed", name)
        envelope = _error_envelope(name, exc)
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _startup_banner() -> None:
    """Print tier + tool-count banner to stderr.

    Anonymous users see the upgrade path *before* hitting a 429. Pro users
    see confirmation that their key is being sent. Both surface the
    sibling Korea MCP because one $29/mo key unlocks both.

    Silence with `VIVORY_MCP_QUIET=1` for embedding in IDE logs.
    """
    import os
    if os.environ.get("VIVORY_MCP_QUIET", "").strip() in ("1", "true", "yes"):
        return
    has_key = client.get_api_key() is not None
    base = client.get_api_base()
    tool_count = len(TOOLS)
    if has_key:
        print(
            f"[vivory-mcp-verification] {tool_count} tools | Pro tier (Bearer key sent) | "
            f"gateway={base} | Korean sources are bundled inside verdicts (kor_law_currency, kor_company_status, doi_retraction_status, …)",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"[vivory-mcp-verification] {tool_count} tools | Anonymous tier (100/day per IP) | "
            f"gateway={base}\n"
            f"  → Tools Pro bridge ($4.99/mo, 1k call/mo) or Vivory API Pro\n"
            f"    ($29/mo USDC, 10k/day, no auto-renew, no custody) at\n"
            f"    https://api.vivory.app/dashboard/public-api — Korean sources\n"
            f"    are bundled inside verdicts (kor_law_currency, kor_company_status,\n"
            f"    doi_retraction_status, …).",
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
