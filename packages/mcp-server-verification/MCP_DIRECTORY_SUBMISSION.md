# MCP Directory submission — vivory-mcp-verification

> **State as of 2026-05-20**: `vivory-mcp-verification` **v0.5.1 LIVE on PyPI + MCP Registry**. 53 tools / 22 categories. Install: `uvx vivory-mcp-verification`. (v0.5.0 was rejected by PyPI 512c summary limit + a mirror race put the pre-trim commit under the v0.5.0 tag → 0.5.1 ships the trimmed description.) Remaining operator action = open the two awesome-mcp-servers PRs.

Submission packet for [MCP Registry](https://registry.modelcontextprotocol.io)
+ punkpeye/awesome-mcp-servers + wong2/awesome-mcp-servers.

## Server identity

- **Name**: `vivory-verification`
- **MCP Registry ID**: `io.github.jayjodev/vivory-mcp-verification`
- **Package**: [`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/) on PyPI (latest live: v0.5.1)
- **Maintainer**: Vivory (contact@vivory.app)
- **License**: MIT
- **Source (public mirror)**: https://github.com/jayjodev/vivory-mcp (subpath `packages/mcp-server-verification`)
- **Sister package**: [`vivory-mcp-korea`](https://pypi.org/project/vivory-mcp-korea/) — 55 Korean public-data tools, **shares the same Pro API key**

## One-line pitch

Umbrella MCP server for verifiable AI work — one registration for 53 tools across 22 categories (claim · DOI · archive · repro · provenance · peer review · forecast · SEC EDGAR · GLEIF · Wikidata · ClinicalTrials · World Bank · USPTO · OSM · DefiLlama · USGS · MOLIT real-estate).

## Category

Verification / Reference / Citation / Provenance

## Why this server is unique

The MCP Directory has no general-purpose verification server. Agents that
cite things end up wiring Crossref + Wayback + SEC EDGAR + GLEIF + a
half-baked C2PA reader by hand. This server gives them a single registration
for the entire "is this real?" stack:

- **53 tools across 22 categories** (claim, DOI, archive, repro hash, C2PA/PDF/hash-chain/watermark provenance, peer-review verdicts, forecast track record, SEC EDGAR, GLEIF LEI, OpenAlex works, Wikidata Q-numbers, ClinicalTrials NCT, World Bank, USPTO PatentsView, OSM places, DefiLlama TVL, USGS quakes, MOLIT Korean real-estate)
- **65 of 69 backing endpoints are v0.1-real** (the remaining 4 are forecast/repro scaffolds shipping in v0.5)
- Free anonymous tier (100/day/IP) — no signup gate
- **Unified Pro key** — $29/mo unlocks both `vivory-mcp-verification` AND `vivory-mcp-korea` (100+ tools, one purchase). USDC + card (Stripe/Lemon Squeezy)
- Self-hostable: `VIVORY_API_BASE` env var redirects to your own gateway

## Install + register

```bash
uvx vivory-mcp-verification
# or
pip install vivory-mcp-verification
```

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification"
    }
  }
}
```

## Tool clusters (18 categories, 45 tools)

| Cluster | Tools | Backing |
|---|---|---|
| claim | verify_claim, extract_citations, archive_claim_sources | v0.1-real |
| doi | verify_doi, doi_metadata, doi_retraction_check, doi_author_network | v0.1-real (Crossref + OpenAlex + ORCID) |
| archive | verify_archive, wayback_capture, wayback_history | v0.1-real (Wayback) |
| repro | verify_repro_hash, repro_hub_lookup, repro_artifact_diff | v0.1-real (Vivory Reproducibility Hub) |
| provenance | verify_c2pa, verify_pdf_provenance, verify_hash_chain, verify_timestamp, detect_watermark | v0.1-real |
| peer-review | verify_peer_review, persona_verdict_lookup | v0.1-real |
| forecast | forecast_track_record, submit_forecast | v0.1-scaffold (Phase 3) |
| entity | sec_edgar_lookup, sec_edgar_filings, gleif_lei_lookup, gleif_lei_match | v0.1-real |
| work | openalex_work, openalex_author | v0.1-real |
| wikidata | wikidata_qnumber, wikidata_property | v0.1-real |
| trial | clinicaltrials_lookup, clinicaltrials_search | v0.1-real |
| indicator | worldbank_indicator, worldbank_country | v0.1-real |
| patent | uspto_patent, uspto_search | v0.1-real |
| place | osm_place, osm_geocode | v0.1-real |
| tvl | defillama_protocol, defillama_chain | v0.1-real |
| quake | usgs_quake, usgs_recent | v0.1-real |
| apt | molit_apt_realtransaction (Korean apartment prices) | v0.1-real |

## Demo workflow (for review)

Classic agent failure mode: cite a DOI without checking it's still valid.
Fix with `vivory-verification`:

1. Agent generates a paragraph that cites `10.1038/s41586-021-03819-2`.
2. `verify_doi` → status: active, type: journal-article.
3. `doi_retraction_check` → retracted: false.
4. `doi_author_network` (depth=1) → ORCID-validated author list with institutions.
5. Agent surfaces the citation with a Vivory verification receipt URL.

Total: 3 tool calls, 0 hallucinations, full source trail.

## Tier model

| Tier      | Quota         | Cost                       |
|-----------|---------------|----------------------------|
| Anonymous | 100/day/IP    | Free, no signup            |
| Free      | 500/day       | Free, signup at api.vivory.app/dashboard |
| Pro       | 10,000/day    | $29/mo USDC or card (x402 capable); same key unlocks `vivory-mcp-korea` |

Mission: anti-mission #1 (no enterprise sales) — Pro is self-serve flat
USDC/card, not a sales-gated SaaS contract.

## Sample envelope

```json
{
  "implementation_phase": "v0.1-real",
  "checked_at": "2026-05-20T18:00:00Z",
  "sources": ["crossref", "openalex"],
  "data": {
    "doi": "10.1038/s41586-021-03819-2",
    "status": "active",
    "title": "Highly accurate protein structure prediction with AlphaFold",
    "type": "journal-article",
    "publisher": "Springer Science and Business Media LLC",
    "year": 2021,
    "container_title": "Nature",
    "is_referenced_by_count": 12048
  }
}
```

## Roadmap

- **v0.5.x (now)**: 53 tools across 22 categories, 49 fully real / 4 envelope-ready (forecast + repro scaffolds). New in v0.5: Identity (ORCID), Web (URL hash + dataset fingerprint), Domain (RDAP whois + DoH DNS), Chain (EVM blockchain audit).
- **v0.5**: Forecast verifier wired to `crypto.vivory.app/forecast` track record. Repro auto-finalize bound to Reproducibility Hub.
- **v0.6**: Peer Review MCP split candidate (separate registration if traffic justifies — see `project_peer_review_mcp_planning_2026_05_16.md`).

## Contact

- Email: contact@vivory.app
- Public mirror: https://github.com/jayjodev/vivory-mcp
- Issues: https://github.com/jayjodev/vivory-mcp/issues
- Maintainer: Vivory (jayjodev)

---

## Companion submissions (post-PyPI-publish)

Same shape as the `vivory-mcp-korea` packet — submit list 1 first, then list 2 ~3 days later.

### 1️⃣ punkpeye/awesome-mcp-servers

Repo: https://github.com/punkpeye/awesome-mcp-servers
Section: 🔎 **Search & Data Extraction** (best fit) or 🛡️ **Security** (secondary).

Markdown line:
```markdown
- [jayjodev/vivory-mcp-verification](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-verification) 🐍 ☁️ 🏠 - 53 verification tools across 22 categories — claim, DOI (Crossref + retraction watch + ORCID), web archive (Wayback), reproducibility hash, C2PA / PDF / hash-chain / watermark provenance, peer-review verdicts, forecast track record, SEC EDGAR, GLEIF LEI, OpenAlex, Wikidata, ClinicalTrials, World Bank, USPTO, OSM, DefiLlama, USGS, MOLIT realestate. Single registration replaces ad-hoc citation glue. No upstream API keys required. Install: `uvx vivory-mcp-verification`. Ask Claude: *"Verify every DOI in this paragraph and snapshot any URL that's not on Wayback yet."*
```

### 2️⃣ wong2/awesome-mcp-servers

Repo: https://github.com/wong2/awesome-mcp-servers
Section: "Reference / Citation" or "Security" — fall back to "Other".

Markdown line:
```markdown
- [vivory-mcp-verification](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-verification) - 53 verification tools across 22 categories — DOI / Wayback / C2PA / PDF / hash-chain / peer-review / forecast / SEC EDGAR / GLEIF / Wikidata / ClinicalTrials / World Bank / USPTO / OSM / DefiLlama / USGS / MOLIT — under one MCP. Free anonymous tier (100/day/IP).
```

### 3️⃣ MCP Registry — DONE (v0.5.1, 2026-05-20)

Published via `mcp-publisher publish` after `mcp-publisher login github` device flow.
Visible at:
```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=jayjodev" \
  | python3 -m json.tool
```
Future version bumps follow the same flow — bump pyproject + `__init__.py` + `server.json`, push monorepo, tag the public mirror, then `mcp-publisher publish` once PyPI metadata lands.

### 4️⃣ Anthropic official `modelcontextprotocol/servers` — defer

Submission bar = traction signal. Re-evaluate after both awesome lists land + ≥100 stars on `jayjodev/vivory-mcp`.

### Submission checklist (before any PR)

- [x] PyPI package `vivory-mcp-verification==0.5.1` published — `uvx vivory-mcp-verification` works
- [x] GitHub repo `jayjodev/vivory-mcp` public with package directory at `packages/mcp-server-verification/`
- [x] README has `## Tier limits` + sample envelope + `## Sister packages`
- [x] LICENSE file present (MIT)
- [x] Tool count and category list in README accurate (53 / 22)
- [x] `server.json` version matches PyPI release (0.5.1)
- [x] `mcp-publisher publish server.json` executed → visible in registry search
- [ ] PR to punkpeye/awesome-mcp-servers opened
- [ ] PR to wong2/awesome-mcp-servers opened
