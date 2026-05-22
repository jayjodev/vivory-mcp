# vivory-mcp-verification

<!-- mcp-name: io.github.jayjodev/vivory-mcp-verification -->

> **Verifiable AI work — one MCP server for every "is this real?" question.**

An umbrella MCP (Model Context Protocol) server that gives AI agents a single
registration for **98 verification tools** across 36 categories: claim
verification, DOI + ORCID + Crossref Funder + OpenCitations + PubPeer
post-publication review, web archive lookup, URL hash + dataset
fingerprint, reproducibility hash registry, media + document provenance
(C2PA / EXIF / pHash / video / PDF / AI-generator signature / CID v1 /
RFC 3161 timestamp), Universal Peer Review (panel + bulk + stats),
forecast track record + ensemble + calibration, SEC EDGAR, GLEIF,
Wikidata, Wikipedia cite-health, ClinicalTrials.gov, World Bank macro,
OpenStreetMap, DefiLlama TVL, USGS, MOLIT RTMS, RDAP +
DoH DNS, EVM blockchain audit + proxy upgrade poll, npm + PyPI
supply-chain, Retraction Watch, Korean law + KYB (NTS × CSL Verified
Fact corpus), OFAC + UN + EU sanctions, openFDA + CPSC recall, DOAJ
journal quality, PR-vs-article diff, and curated multi-step workflows.

Built by [Vivory](https://vivory.app) — a verifiable AI work platform.
Mission: in an age where everything is synthesized, verification trails become trust.

## What's inside (v0.10.0 — 98 tools / 36 categories)

| Category       | # | What it answers                                                                          |
|----------------|---|------------------------------------------------------------------------------------------|
| Claim          | 3 | Extract / verify / archive citations from arbitrary text                                 |
| DOI            | 4 | Resolve, retraction-check, author network (Crossref + OpenAlex)                          |
| Archive        | 3 | Wayback Machine snapshot lookup, capture, history                                        |
| Repro          | 3 | Vivory Repro Hub hash registry — match, lookup, diff                                     |
| **Provenance** | **13** | C2PA, PDF provenance, hash chain, watermark, RFC 3161 timestamp, EXIF, perceptual hash, video metadata + frame-hash, PDF metadata, file hash, AI-generator signature DB, combined summary — who/when/where/what across image/video/PDF |
| **Peer review**| **5** | Vivory Universal Peer Review — verdict + per-persona + bulk + reviewer panel + stats    |
| Forecast       | 4 | Vivory crypto.vivory.app/forecast track record + submit + Polymarket/Kalshi/Manifold ensemble + ECE/MCE/Brier calibration |
| Filing         | 3 | SEC EDGAR — ticker → CIK, recent filings, XBRL company facts                             |
| Entity         | 3 | GLEIF — LEI lookup, name search, corporate hierarchy                                     |
| Work           | 3 | OpenAlex academic works + citation graph + salami-slicing near-dup screen                |
| Wikidata       | 2 | Q-number entity grounding — global hallucination backbone                                |
| Trial          | 2 | ClinicalTrials.gov v2 — NCT registry verify + search                                     |
| Indicator      | 2 | World Bank Open Data — macro indicators + time series                                    |
| Place          | 2 | OpenStreetMap Nominatim — geo verification by ID / coords / name                         |
| TVL            | 2 | DefiLlama — crypto protocol + chain TVL verification                                     |
| Quake          | 2 | USGS Earthquake — seismic event verification                                             |
| Apt            | 2 | MOLIT RTMS — Korean apartment real-transaction prices (sigungu × month × trade/rent)     |
| Identity       | 2 | ORCID author identity — resolve iD to name + works, chain into DOI verdicts              |
| Web            | 2 | URL hash + dataset fingerprint — sha256 + size + ETag + structure probe                  |
| Domain         | 4 | RDAP whois + Cloudflare DoH DNS + owner-change + WHOIS history                           |
| Chain          | 4 | EVM blockchain audit envelope + contract-admin activity + proxy-upgrade poll (Eth/Arb/Base/Op/Polygon) |
| npm            | 2 | Package metadata + maintainer history + typosquat heuristic                              |
| PyPI           | 2 | Package metadata + maintainer history + typosquat heuristic                              |
| Retraction     | 3 | Retraction Watch DOI status + recent retractions + by-journal feed                       |
| Workflow       | 3 | Curated multi-step recipes — paper repro, crypto diligence, AI-output verify             |
| Policy         | 2 | Custom verification policy framework — list presets + evaluate                           |
| **Law (KR)**   | **5** | NTS × CSL Verified Fact corpus — law lookup + currency + case search + bill status + company KYB |
| Sanctions      | 1 | OFAC + UN + EU + KR STIC consolidated screen (via OpenSanctions)                         |
| Recall         | 2 | openFDA drug recall + CPSC SaferProducts consumer-product recall                         |
| Journal        | 1 | DOAJ whitelist + predatory-publisher heuristic                                           |
| PR diff        | 1 | Press-release vs published-article fidelity diff (local n-gram)                          |
| PubPeer        | 1 | Post-publication peer-review commentary on a DOI                                         |
| OpenCitations  | 1 | COCI citation context + self-citation count                                              |
| Funder         | 1 | Crossref Funder Registry resolver (grant chain provenance)                               |
| Wikipedia      | 1 | External-link liveness audit for a Wikipedia article                                     |

Per-tool name list: see [`src/vivory_mcp_verification/server.py`](src/vivory_mcp_verification/server.py)
module docstring (the source-of-truth catalog).

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
[https://api.vivory.app/dashboard](https://api.vivory.app/dashboard)
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

## Drop into your agent

Ready-to-copy recipes that wire Vivory verification into the most common
agent stacks:

| Agent stack            | Recipe                                                                        |
|------------------------|-------------------------------------------------------------------------------|
| Claude Code subagent   | [`examples/claude-code-verify-before-publish.md`](examples/claude-code-verify-before-publish.md) |
| Cursor rule            | [`examples/cursor-verify.mdc`](examples/cursor-verify.mdc)                    |
| LangGraph node         | [`examples/langgraph-verification-node.py`](examples/langgraph-verification-node.py) |
| Plain MCP client       | [`examples/quickstart.md`](examples/quickstart.md)                            |

Each recipe is small (~30–60 lines), MIT-licensed, and battle-tested
against the live `api.vivory.app` gateway. Use them as-is or fork the
checks to your workflow.

## Tier limits — Vivory API Pro

| Tier        | Daily quota  | Notes                                              |
|-------------|--------------|----------------------------------------------------|
| Anonymous   | 100/day/IP   | No signup, polite caching                          |
| Free        | 500/day      | Sign up at api.vivory.app/dashboard                |
| Pro         | 10,000/day   | $29/mo USDC (CoolWallet · Arbitrum) or card. 31-day pass, no auto-renew, no custody. Same key also extends REST gateway quotas at `api.vivory.app/api/public-tools/*` (Korean public-data passthroughs that used to live in the retired `vivory-mcp-korea`). |
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
- `v0.1-scaffold` — envelope shape stable, backing service ships in a later release

Every tool returns its own phase so an agent can branch on it. The
live count per phase is exposed at
[https://api.vivory.app/api/verify/manifest](https://api.vivory.app/api/verify/manifest)
and never needs a package upgrade to stay in sync.

## Error envelope (so agents can branch)

When a tool name is unknown or an upstream call fails, the MCP returns a
structured envelope instead of raising:

```json
{
  "error": "ConnectionError: ...",
  "code": "RATE_LIMIT|AUTH|TIMEOUT|NOT_FOUND|VALIDATION|UPSTREAM|UNKNOWN_TOOL",
  "tool": "verify_doi",
  "gateway": "vivory-mcp-verification",
  "did_you_mean": ["verify_dataset_fingerprint"]
}
```

Branch on `code` (stable) — not the human `error` string.

## Self-hosting

Set `VIVORY_API_BASE` to point at your own gateway (the backend is open
source — `src/backend/app/routers/verify.py` in
[jayjodev/vivory](https://github.com/jayjodev/vivory)).

```bash
VIVORY_API_BASE=https://my-gateway.example.com/api vivory-mcp-verification
```

## The Vivory MCP family

- **vivory-mcp-verification** (this package) — 98 universal verification
  tools across 36 categories. Korean public sources are bundled inside
  verdict evidence (`kor_law_currency`, `kor_company_status`,
  `doi_retraction_status`, …) instead of as a separate Korea-only MCP.
- **vivory-mcp-korea** — **retired 2026-05-21.** v0.6.0 ships a single
  `deprecation_notice` tool. Raw Korean-public-data passthrough was
  removed because re-distributing third-party data mismatched the
  *verifiable-AI-work* motto. The Korean sources are still accessible
  as REST endpoints at `api.vivory.app/api/public-tools/*` (free
  anonymous 100/day per IP).

## License

MIT.

## Links

- Vivory: [https://vivory.app](https://vivory.app)
- Verification Gateway: [https://api.vivory.app](https://api.vivory.app)
- Source: [https://github.com/jayjodev/vivory](https://github.com/jayjodev/vivory)
- Issues: [https://github.com/jayjodev/vivory-mcp/issues](https://github.com/jayjodev/vivory-mcp/issues)
