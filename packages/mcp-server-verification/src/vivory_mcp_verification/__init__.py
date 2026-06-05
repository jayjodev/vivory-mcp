"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.14.0 ships 13 tools across 4 categories
(the moat collapse — see below).

Cluster history:
- v0.10.0: provenance cluster expanded 4→13 (Phase A standards-backed
  who/when/where/what verification across image/video/PDF: EXIF +
  perceptual hash + video ffprobe + video frame hash + PDF metadata +
  file hash + CID v1 + AI generator signature lookup + combined
  provenance summary + RFC 3161 timestamp wrapper).
- v0.11.0: reconcile cluster (Crossref + OpenAlex + Semantic Scholar +
  arXiv with deterministic provenance hash) — 98→101 tools.
- v0.11.1: USPTO PatentsView cluster retired (2026-05-29 decommission
  pre-emptive) — 101→99 tools.
- v0.11.2: stale sibling-package references corrected. vivory-mcp-korea
  and vivory-mcp-kosis are deprecated; Korean verdict tools (kor_law_*,
  kor_company_status, doi_retraction_status, …) live in this package.
  Dead "key unlocks Korea MCP" marketing removed from banner/server.json.
- v0.12.0: retired 10 low-uptake tools (4 Tier-U composers +
  6 parity-debt MCP-only without web siblings) — 99→89 tools,
  36→34 categories.
- v0.13.0: retired 2 forecast tools (forecast_track_record,
  submit_forecast) — surface-coupled to the retired vivory.app/forecast
  Hub sub-route (2026-06-04). 89→87 tools.
- v0.14.0: **moat collapse** (2026-06-05). The agent surface narrows
  to what only Vivory can offer — 87→13 tools, 34→4 categories:
    · law (5) — Korean public-data verdicts (the moat)
    · reconcile (3) — deterministic-provenance-hash cross-source engine
    · doi (2) — research-integrity anchor (verdict + retraction gate)
    · provenance (3) — offline-verifiable receipt backbone
  Dropped ~74 commodity public-API wrappers (LEI, SEC EDGAR, World
  Bank, USGS, DefiLlama, Wikidata, ClinicalTrials, ORCID, npm/PyPI,
  sanctions, archive/wayback, …) and surface-internal tools
  (repro·peer-review → the now-personal Repro Hub; forecast → retired
  forecast surface). Web Tools keep their breadth as an SEO discovery
  funnel; the parity invariant is decoupled to `web ⊇ MCP`.

All Phase A tools are standards-only — no ML inference, no new Python
deps, no new system binaries beyond ffmpeg/ffprobe. Honest about scope:
signature match only, absence of match does NOT prove human-created.

See `vivory_mcp_verification.server` module docstring for the full
cluster list. All tools are HTTP wrappers over `api.vivory.app/api/verify/*`
and adjacent endpoints (`/api/blockchain-audit/*`). The backend handles
caching, attribution, and upstream auth. The MCP layer translates LLM
tool calls into HTTP GETs/POSTs.

Tier:
- Anonymous   — 100/day per IP, no signup
- Tools Pro   — $4.99/mo, 10,000 calls/day across all 13 verification tools
                (single paid tier after bundle absorb 2026-06-01; the prior
                standalone $29/mo Vivory API Pro tier is retired). USDC or
                card (Stripe / Lemon Squeezy), no auto-renew, no custody.
                Sibling vivory-mcp-korea and vivory-mcp-kosis are deprecated
                — Korean verdict tools (kor_law_currency, kor_company_status,
                doi_retraction_status, …) live in this package.
"""

__version__ = "0.14.0"
