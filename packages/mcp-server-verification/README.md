# vivory-mcp-verification

<!-- mcp-name: io.github.jayjodev/vivory-mcp-verification -->

> **Verifiable AI work — one MCP server for every "is this real?" question.**

An umbrella MCP (Model Context Protocol) server that gives AI agents a single
registration for **45 verification tools** across 18 categories: claim
verification, DOI resolution, web archive lookup, reproducibility hash
registry, media + document provenance, peer-review verdict, forecast track
record, SEC EDGAR filings, GLEIF Legal Entity Identifier, OpenAlex works,
Wikidata Q-numbers, ClinicalTrials.gov, World Bank macro indicators, USPTO
patents, OpenStreetMap places, DefiLlama TVL, USGS earthquakes, and MOLIT
Korean apartment real-transaction prices.

Built by [Vivory](https://vivory.app) — a verifiable AI work platform.
Mission: when AI generates the world, agents need to know what's real.

## What's inside (v0.4.0 — 45 tools)

| Category    | Tools (count) | What it answers                                                      |
|-------------|---------------|----------------------------------------------------------------------|
| Claim       | 3             | Extract / verify / archive citations from arbitrary text             |
| DOI         | 4             | Resolve, retraction-check, author network (Crossref + OpenAlex)      |
| Archive     | 3             | Wayback Machine snapshot lookup, capture, history                    |
| Repro       | 3             | Vivory Repro Hub hash registry — match, lookup, diff                 |
| Provenance  | 4             | C2PA, PDF metadata, hash chain, AI-watermark detection               |
| Peer review | 2             | Vivory Research peer-review verdict + per-persona lookup             |
| Forecast    | 2             | Vivory forecast track record + agent submission                      |
| Filing      | 3             | SEC EDGAR — ticker → CIK, recent filings, XBRL company facts         |
| Entity      | 3             | GLEIF — LEI lookup, name search, corporate hierarchy                 |
| Work        | 2             | OpenAlex academic works + citation graph (sister of DOI)             |
| Wikidata    | 2             | Q-number entity grounding — global hallucination backbone            |
| Trial       | 2             | ClinicalTrials.gov v2 — NCT registry verify + search                 |
| Indicator   | 2             | World Bank Open Data — macro indicators + time series                |
| Patent      | 2             | USPTO PatentsView — US patent registry (sister of KIPRIS)            |
| Place       | 2             | OpenStreetMap Nominatim — geo verification by ID / coords / name     |
| TVL         | 2             | DefiLlama — crypto protocol + chain TVL verification                 |
| Quake       | 2             | USGS Earthquake — seismic event verification                         |
| Apt         | 2             | MOLIT RTMS — Korean apartment real-transaction prices (매매·전월세). Aggregate stats + claim verification. Raw transaction lists + price trend live in sister `vivory-mcp-korea` (`molit_*`). Same data, different axes. |

### Full tool list

**Claim**: `verify_claim` · `extract_citations` · `archive_claim_sources`

**DOI**: `verify_doi` · `doi_metadata` · `doi_retraction_check` · `doi_author_network`

**Archive**: `verify_archive` · `wayback_capture` · `wayback_history`

**Repro**: `verify_repro_hash` · `repro_hub_lookup` · `repro_artifact_diff`

**Provenance**: `verify_c2pa` · `verify_pdf_provenance` · `verify_hash_chain` · `detect_watermark`

**Peer review**: `verify_peer_review` · `persona_verdict_lookup`

**Forecast**: `forecast_track_record` · `submit_forecast`

**Filing**: `verify_filing` · `filing_recent` · `filing_facts`

**Entity**: `verify_lei` · `entity_search` · `entity_relationships`

**Work**: `verify_work` · `search_works`

**Wikidata**: `verify_qid` · `wikidata_search`

**Trial**: `verify_trial` · `trial_search`

**Indicator**: `verify_indicator` · `indicator_series`

**Patent**: `verify_patent` · `patent_search`

**Place**: `verify_place` · `place_search`

**TVL**: `verify_protocol_tvl` · `verify_chain_tvl`

**Quake**: `verify_quake` · `recent_quakes`

**Apt**: `apt_market_snapshot` · `verify_apt_price` (MOLIT RTMS — sigungu × month × {trade, rent}, daily nationwide ingest from 국토교통부)

## Why this exists

Modern AI agents generate citations, summaries, claims, forecasts. Most of
them aren't checked. The few that are checked use whatever ad-hoc lookup
the agent happens to know about — Crossref for one DOI, Wayback for one
URL, a half-implemented C2PA reader for one image. Every agent re-invents
the verification stack.

Vivory's bet: a single MCP server with 20+ verification tools, all wrapping
`api.vivory.app/api/verify/*` (free anonymous tier, Pro $29/mo USDC for
heavier rate limits). One install, one registration, and your agent can:

- ask whether a paragraph's citations resolve;
- check if a DOI was retracted *before* citing it;
- snapshot a URL to Wayback before linking it;
- match a notebook hash against the Vivory Repro Hub registry;
- inspect an image for C2PA provenance + AI watermarks;
- look up a peer-review verdict on a Vivory Research article;
- register a forecast and pick up the verdict at deadline.

## Install

```bash
pip install vivory-mcp-verification
```

Or using `uv`:

```bash
uv pip install vivory-mcp-verification
```

The package auto-installs the `vivory-mcp-verification` script.

## Use with Claude Code / Claude Desktop

Add to your MCP config (`~/.claude/mcp.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification"
    }
  }
}
```

For a higher rate limit, sign up at
[https://api.vivory.app/dashboard/api-keys](https://api.vivory.app/dashboard/api-keys)
and add the key:

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification",
      "env": {
        "VIVORY_API_KEY": "vk_live_..."
      }
    }
  }
}
```

## Use with `claude mcp add` (Claude Code CLI)

```bash
claude mcp add vivory-verification vivory-mcp-verification
```

## Tier limits — Vivory API Pro

**One $29/mo key unlocks BOTH MCPs.** A Pro key issued for `vivory-mcp-verification`
also unlocks `vivory-mcp-korea` (55 Korean public-data tools) and vice versa —
the same Bearer credential is honored across the entire Vivory MCP family.

| Tier        | Daily quota  | Notes                                              |
|-------------|--------------|----------------------------------------------------|
| Anonymous   | 100/day/IP   | No signup, polite caching                          |
| Free        | 500/day      | Sign up at api.vivory.app/dashboard/api-keys       |
| Pro         | 10,000/day   | $29/mo USDC (CoolWallet · Arbitrum) or card. 31-day pass, no auto-renew, no custody. Same key unlocks `vivory-mcp-korea` (55 tools) = **100+ tools, one purchase**. |
| Enterprise  | 100,000/day  | contact@vivory.app (self-serve only, no SaaS sales) |

Sign up at **[api.vivory.app/dashboard/public-api](https://api.vivory.app/dashboard/public-api)**.

Heavy tools (`doi_author_network` depth=2, `verify_claim` mode=thorough,
`repro_artifact_diff`) count as 5 calls each.

## How verification verdicts work

Every endpoint returns a uniform envelope:

```json
{
  "implementation_phase": "v0.1-real",
  "checked_at": "2026-05-06T18:00:00Z",
  "sources": ["crossref", "openalex"],
  "data": { ... },
  "note": null
}
```

`implementation_phase` is the contract:

- `v0.1-real`     — full implementation, results trustworthy
- `v0.1-partial`  — partial (e.g. core works, advanced sub-feature pending)
- `v0.1-scaffold` — envelope shape stable, backing service ships in v0.2

Real today: extract_citations · hash_chain (sha256) · verify_doi · doi_metadata
· doi_retraction_check · doi_author_network (depth=1) · verify_archive ·
wayback_history · verify_filing · filing_recent · filing_facts · verify_lei
· entity_search · entity_relationships · verify_work · search_works ·
verify_qid · wikidata_search · verify_trial · trial_search · verify_indicator
· indicator_series · verify_patent · patent_search · verify_place ·
place_search · verify_protocol_tvl · verify_chain_tvl · verify_quake ·
recent_quakes.

Scaffold today (envelope ready, full backing in a later release): verify_claim
full pipeline · archive_claim_sources batch capture · wayback_capture SPN2
dispatch · repro lookup · c2pa · pdf-provenance · watermark · peer-review
verdict · forecast submit.

## Self-hosting

Set `VIVORY_API_BASE` to point at your own gateway (the backend is open
source — `src/backend/app/routers/verify.py` in
[jayjodev/vivory](https://github.com/jayjodev/vivory)).

```bash
VIVORY_API_BASE=https://my-gateway.example.com/api vivory-mcp-verification
```

## Sister packages in the Vivory MCP family

- **[vivory-mcp-korea](https://pypi.org/project/vivory-mcp-korea/)** —
  Korean public data (KOSIS / BoK / DART / NEIS / Opinet / KMA / 14 sources,
  51 tools).
- **vivory-mcp-verification** — this package (verification, 45 tools
  spanning DOI/Crossref/OpenAlex, web archive, SEC EDGAR + GLEIF + USPTO
  as global sisters to DART/KIPRIS, Wikidata grounding, ClinicalTrials.gov,
  World Bank macro, OpenStreetMap, DefiLlama, USGS earthquake, MOLIT RTMS
  Korean apartment real-transaction prices).
- More coming under the same `api.vivory.app` umbrella.

## License

MIT.

## Links

- Vivory: [https://vivory.app](https://vivory.app)
- Verification Gateway: [https://api.vivory.app](https://api.vivory.app)
- Source: [https://github.com/jayjodev/vivory](https://github.com/jayjodev/vivory)
- Issues: [https://github.com/jayjodev/vivory-mcp/issues](https://github.com/jayjodev/vivory-mcp/issues)
