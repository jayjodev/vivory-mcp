# MCP Directory submission — vivory-mcp-verification

> **State as of 2026-05-13 evening**: package is **v0.4.0 / 45 tools / 18 categories**. PyPI publish is still pending; see [`docs/handoffs/MCP_PUBLISH_RUNBOOK_2026_05_13.md`](../../docs/handoffs/MCP_PUBLISH_RUNBOOK_2026_05_13.md) for current operator action. The body of this packet still uses older numbers in some spots — update before opening the actual PR.

Submission packet for [Anthropic MCP Directory](https://github.com/anthropics/mcp-directory)
+ punkpeye/awesome-mcp-servers + wong2/awesome-mcp-servers.

## Server identity

- **Name**: `vivory-verification`
- **Package**: `vivory-mcp-verification` on PyPI
- **Maintainer**: Vivory (contact@vivory.app)
- **License**: MIT
- **Source**: https://github.com/jayjodev/vivory (subpath `src/mcp-server-verification`)
- **Sister package**: [`vivory-mcp-korea`](https://pypi.org/project/vivory-mcp-korea/) (already in directory)

## One-line pitch

Umbrella MCP server for verifiable AI work — one registration for 21 verification tools (claim · DOI · archive · repro · provenance · peer review · forecast).

## Category

Verification / Reference / Citation

## Why this server is unique

The MCP Directory has nothing in the verification category. Everyone who
builds an agent that cites things ends up wiring Crossref + Wayback + a
half-baked C2PA reader by hand. This server gives them a single registration
for the entire stack:

- 21 tools across 7 categories
- Real-time backing for DOI / Crossref / OpenAlex / Wayback (no API key needed)
- Forward-compatible scaffold for C2PA / PDF / repro / peer-review / forecast
  (envelope shape stable; backing services ship in v0.2)
- Free anonymous tier (100/day/IP) — no signup gate
- Self-hostable: `VIVORY_API_BASE` env var redirects to your own gateway

## Install + register

```bash
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

## Tool list (21)

```
verify_claim, extract_citations, archive_claim_sources,
verify_doi, doi_metadata, doi_retraction_check, doi_author_network,
verify_archive, wayback_capture, wayback_history,
verify_repro_hash, repro_hub_lookup, repro_artifact_diff,
verify_c2pa, verify_pdf_provenance, verify_hash_chain, detect_watermark,
verify_peer_review, persona_verdict_lookup,
forecast_track_record, submit_forecast
```

## Demo workflow (for review)

The classic agent failure mode: cite a DOI without checking it's still
valid. Here's how an agent fixes that with vivory-verification:

1. Agent generates a paragraph that cites `10.1038/s41586-021-03819-2`.
2. Agent calls `verify_doi` → status: active, type: journal-article.
3. Agent calls `doi_retraction_check` → retracted: false.
4. Agent calls `doi_author_network` (depth=1) → returns ORCID-validated
   author list with institutions.
5. Agent surfaces the citation in its output with a Vivory verification
   receipt URL.

Total: 3 tool calls, 0 hallucinations, full source trail.

## Tier model

| Tier      | Quota         | Cost                       |
|-----------|---------------|----------------------------|
| Anonymous | 100/day/IP    | Free, no signup            |
| Free      | 500/day       | Free, signup               |
| Pro       | 10,000/day    | $29/mo USDC (x402 capable) |

Mission: anti-mission #1 (no enterprise sales) — Pro is self-serve flat
USDC, not a sales-gated SaaS contract.

## Sample envelope

```json
{
  "implementation_phase": "v0.1-real",
  "checked_at": "2026-05-06T18:00:00Z",
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

- **v0.1 (now)**: 21 tools shipping, 8 fully real / 13 envelope-ready.
- **v0.2**: Wire C2PA (c2patool subprocess), PDF provenance (pypdf), watermark
  detectors (invisible-watermark + SynthID surface), Repro Hub DB lookup,
  Peer Review DB lookup.
- **v0.3**: Forecast Verify pipeline (intel.forecast write-path + auto-verifier
  scheduling). Targeted at Phase 3 of the Vivory MCP family carrier.
- **v1.0**: All 21 tools real, x402 M2M billing live, Pro tier USDC payment.

## Contact

- Email: contact@vivory.app
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
- [jayjodev/vivory-mcp-verification](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-verification) 🐍 ☁️ 🏠 - 21 verification tools across 7 categories — claim, DOI (Crossref + retraction watch + ORCID author network), web archive (Wayback + archive.today), reproducibility hash registry, C2PA / PDF / hash-chain provenance, peer-review verdict, forecast track record. Single registration replaces ad-hoc Crossref + Wayback + half-baked C2PA glue. No upstream API keys required. Install: `uvx vivory-mcp-verification`. Ask Claude: *"Verify every DOI in this paragraph and snapshot any URL that's not on Wayback yet."*
```

### 2️⃣ wong2/awesome-mcp-servers

Repo: https://github.com/wong2/awesome-mcp-servers
Section: "Reference / Citation" or "Security" — fall back to "Other".

Markdown line:
```markdown
- [vivory-mcp-verification](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-verification) - 21 verification tools — DOI / Wayback / C2PA / PDF / hash-chain / peer-review / forecast — under one MCP. Free anonymous tier (100/day/IP).
```

### 3️⃣ Anthropic official `modelcontextprotocol/servers` — defer

Submission bar = PyPI release + traction. Re-evaluate after both lists land + ≥100 stars on `jayjodev/vivory-mcp`.

### Submission checklist (before any PR)

- [ ] PyPI package `vivory-mcp-verification==0.1.0` published — `uvx vivory-mcp-verification` works
- [x] GitHub repo `jayjodev/vivory-mcp` is public with package directory at `packages/mcp-server-verification/`
- [x] README has `## Tier limits` + sample envelope + `## Sister packages`
- [x] LICENSE file present (MIT)
- [ ] Self-test: fresh `pip install vivory-mcp-verification` reports tools=21, handlers=21, parity=True
- [x] Tool count and source list in README accurate (21 / 7 categories)
