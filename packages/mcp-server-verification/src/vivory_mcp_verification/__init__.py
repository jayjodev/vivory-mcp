"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.5 ships 53 tools across 22 categories:

- Claim       — extract / verify / archive citations from arbitrary text
- DOI         — resolve, retraction-check, author network (Crossref + OpenAlex)
- Archive     — Wayback / archive.today snapshot lookup + capture
- Repro       — Vivory Repro Hub hash registry lookup + diff
- Provenance  — C2PA, PDF metadata, hash chain, watermark detect
- Peer review — Vivory Research peer-review verdict lookup
- Forecast    — Vivory forecast track record (crypto.vivory.app/forecast) + agent submit
- Filing      — SEC EDGAR filings (10-K / 10-Q / 8-K) + XBRL facts
- Entity      — GLEIF Legal Entity Identifier resolve / search / relationships
- Work        — OpenAlex academic work + author citation graph
- Wikidata    — Q-number entity grounding (global hallucination backbone)
- Trial       — ClinicalTrials.gov v2 medical trial verification
- Indicator   — World Bank Open Data macro indicators + time series
- Patent      — USPTO PatentsView US patent registry
- Place       — OpenStreetMap Nominatim geo entity verification
- TVL         — DefiLlama crypto protocol + chain TVL verification
- Quake       — USGS Earthquake seismic event verification
- Apt         — MOLIT RTMS Korean apartment real-transaction prices (sigungu × month, daily nationwide ingest)
- Identity    — ORCID author identity resolve + works list
- Web         — URL hash + dataset fingerprint with structure probe
- Domain      — RDAP whois + Cloudflare DoH DNS
- Chain       — EVM transaction signed audit envelope (Ethereum, Arbitrum, Base, Optimism, Polygon)

All tools are HTTP wrappers over `api.vivory.app/api/verify/*` and
adjacent endpoints (`/api/blockchain-audit/*`). The backend handles
caching, attribution, and upstream auth. The MCP layer translates LLM
tool calls into HTTP GETs/POSTs.
"""

__version__ = "0.5.1"
