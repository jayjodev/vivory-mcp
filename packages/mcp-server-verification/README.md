# vivory-mcp-verification

<!-- mcp-name: io.github.jayjodev/vivory-mcp-verification -->

> **Receipts on products, sources on content — one MCP server for every "is this real?" question.**

An umbrella MCP (Model Context Protocol) server that gives AI agents a single
registration for **13 verification tools** across 4 categories — the **moat**:
what only Vivory can offer. Korean public-data verdicts (국가법령정보센터 +
열린국회정보 + NTS × CSL Verified Fact corpus), a deterministic-provenance-hash
cross-source reconcile engine, a DOI verdict + retraction gate, and an
offline-verifiable receipt backbone (C2PA + content hash + hash chain).

> **v0.14.0 moat collapse (2026-06-05)** narrowed the agent surface 87 → 13,
> dropping ~74 commodity public-API wrappers (LEI, SEC EDGAR, World Bank,
> USGS, DefiLlama, Wikidata, ClinicalTrials, ORCID, npm/PyPI, sanctions,
> archive/wayback, …) and surface-internal tools (repro/peer-review → the
> now-personal Repro Hub; forecast → the retired forecast surface). The
> tools.vivory.app **web** catalog keeps its breadth as an SEO discovery
> funnel — the parity invariant is decoupled to `web ⊇ MCP`.

Built by [Vivory](https://vivory.app) — a verifiable AI work platform.
Mission: **See for yourself.**

## What's inside (v0.14.0 — 13 tools / 4 categories)

| Category       | # | What it answers                                                                          |
|----------------|---|------------------------------------------------------------------------------------------|
| **Law (KR)**   | **5** | NTS × CSL Verified Fact corpus — law lookup + currency + case search + bill status + company KYB (the Korean public-data moat) |
| **Reconcile**  | **3** | Cross-source consensus + deterministic provenance hash — company / recall / person (Vivory-differentiated method) |
| **DOI**        | **2** | `verify_doi` (verdict) + `doi_retraction_check` (retraction gate) — the research-integrity anchor, before an LLM cites |
| **Provenance** | **3** | `verify_c2pa` + `compute_file_hash` + `verify_hash_chain` — the offline-verifiable receipt backbone |

Per-tool name list: see [`src/vivory_mcp_verification/server.py`](src/vivory_mcp_verification/server.py)
module docstring (the source-of-truth catalog).

## Why this exists

Modern AI agents generate citations, summaries, claims. Most aren't checked.
A breadth of thin wrappers over public APIs (Crossref, World Bank, USGS) is
something any agent can already reach — and most never call. So the agent
surface here is **not** breadth; it's the moat: verifications that are
Vivory-only (Korean public-data verdicts), Vivory-differentiated (the
deterministic-provenance-hash reconcile), or the actual product
(an offline-verifiable receipt you can recompute yourself).

Vivory's bet: a single MCP server with 13 verification tools, all wrapping
`api.vivory.app/api/verify/*` (free anonymous tier, Tools Pro $4.99/mo for
heavier rate limits — same key as the tools.vivory.app utility surface
after the 2026-06-01 bundle absorb). One install, one registration, and
your agent can:

- check if a DOI was retracted *before* citing it;
- reconcile a company / person / recall across 2-4 registries with a
  deterministic provenance hash anyone can recompute;
- look up whether a Korean law is still in force, or a company's KYB status;
- inspect an image's C2PA manifest + fingerprint any artifact into a
  receipt (SHA-256 / SHA-512 / IPFS CID) you can verify offline.

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

## Tier limits — Tools Pro key (bundle absorb 2026-06-01)

| Tier        | Daily quota  | Notes                                              |
|-------------|--------------|----------------------------------------------------|
| Anonymous   | 100/day/IP   | No signup, polite caching                          |
| Free        | 500/day      | Sign up at api.vivory.app/dashboard                |
| **Tools Pro** | **10,000/day** | **$4.99/mo** USDC (CoolWallet · Arbitrum) or card. 31-day pass, no auto-renew, no custody. The Tools Pro key authenticates **both** the tools.vivory.app utility surface and the Verification MCP (13 moat tools, Korean verdict tools included). |
| Enterprise  | 100,000/day  | contact@vivory.app (self-serve only, no SaaS sales) |

> **2026-06-01 bundle absorb**: the prior standalone Vivory API Pro
> ($29/mo Verification-only tier) was retired after landscape WTP
> analysis. The Tools Pro $4.99/mo key is now the single paid tier
> across all Vivory paid surfaces.

Sign up at **[tools.vivory.app/pro](https://tools.vivory.app/pro)**.

Heavy tools (`company_reconcile` / `person_reconcile` cross-source fan-out)
count as 5 calls each.

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

- **vivory-mcp-verification** (this package) — 13 moat verification
  tools across 34 categories. Korean public sources are bundled inside
  verdict evidence (`kor_law_currency`, `kor_company_status`,
  `doi_retraction_status`, `kor_case_search`, `kor_bill_status`)
  instead of as a separate Korea-only MCP.
- **vivory-mcp-korea** — **retired 2026-05-21** (v0.6.2 deprecation-only).
  Raw Korean-public-data passthrough was removed because re-distributing
  third-party data mismatched the *verifiable-AI-work* motto and several
  upstream source ToS. The REST gateway at `api.vivory.app/api/public-tools/*`
  went cluster-internal on 2026-05-22 — external callers no longer have
  a Korean raw-data surface from Vivory.
- **vivory-mcp-kosis** — **retired 2026-05-28** (v0.1.4 deprecation-only).
  Original standalone KOSIS wrapper; superseded by the same migration path.

## License

MIT.

## Links

- Vivory: [https://vivory.app](https://vivory.app)
- Verification Gateway: [https://api.vivory.app](https://api.vivory.app)
- Source: [https://github.com/jayjodev/vivory](https://github.com/jayjodev/vivory)
- Issues: [https://github.com/jayjodev/vivory-mcp/issues](https://github.com/jayjodev/vivory-mcp/issues)
