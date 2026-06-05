# vivory-mcp-korea — ⚠️ DEPRECATED v0.6.2

<!-- mcp-name: io.github.jayjodev/vivory-mcp-korea -->

> **This package is deprecated.** Korean raw-data wrappers (KOSIS, BOK, DART, KMA, MOLIT, VWorld, NEIS, HIRA, NMC, Opinet, MFDS, MOIS, NTS, AirKorea, Seoul OpenData, MoE EV) conflicted with Vivory's verifiable-AI-work mission and several upstream source ToS. Migrate to **[`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/)** — Korean verdict tools are bundled there, and the Tools Pro $4.99/mo key authenticates the full 89-tool catalog (bundle absorb 2026-06-01; the prior standalone $29/mo Vivory API Pro tier is retired).
>
> **Migrate in one line:**
>
> ```bash
> uvx vivory-mcp-verification
> ```

---

## Why deprecated

Vivory's mission is **verifiable AI work**, not raw-data redistribution. The umbrella Korean MCP shipped 56 wrappers across 16 upstream APIs. Several of those upstreams (DART bulk filings, NEIS school list, MOLIT raw transactions, VWorld 1,534 venue dump) prohibited bulk redistribution under their terms of service. Rather than litigate per-source, the entire raw-passthrough surface was retired.

Korean public sources are still used inside Vivory — as **underlying evidence for verdicts** in `vivory-mcp-verification`:

| Verdict tool (in vivory-mcp-verification) | Korean source used as evidence |
|---|---|
| `kor_law_currency` | 법령정보센터 (law.go.kr) |
| `kor_company_status` | NTS 사업자등록 + CSL cross-check |
| `kor_case_search` | 대법원 종합법률정보 |
| `kor_bill_status` | 국회 의안정보 |
| `doi_retraction_status` | Crossref + OpenAlex + PubPeer |

This is consistent with Vivory's verifiable-AI-work mission and each source's ToS (evidence for verdicts vs. raw redistribution).

---

## Migration

Update your `claude_desktop_config.json` (or `claude mcp add` invocation) from this:

```json
{
  "mcpServers": {
    "vivory-korea": {
      "command": "uvx",
      "args": ["vivory-mcp-korea"]
    }
  }
}
```

to this:

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "uvx",
      "args": ["vivory-mcp-verification"]
    }
  }
}
```

Same `VIVORY_API_KEY` env var (if set) carries over.

---

## What this release still does

To give existing v0.5.x / v0.6.x users a clear migration signal, the package:

- Ships exactly **one tool** (`vivory_korea_deprecated_migration_notice`) that returns the migration payload.
- Returns the **same deprecation payload** for any other tool name the LLM tries (including the old `kosis_*`, `dart_*`, `kma_*`, `vworld_*`, `nts_*`, …) instead of silently 404ing.
- Prints a loud stderr banner on startup (suppress with `VIVORY_MCP_QUIET=1`).

**v0.6.2 wheel cleanup:** the dead raw-wrapper source modules (`tools/{kosis,bok,dart,kma,airkorea,opinet,hira,nmc,molit,kto,mfds,mois,neis,vworld}.py`, `client.py`) were unreachable since v0.6.0 but still bundled in the wheel. v0.6.2 deletes them — ToS-incompatible source should not ship even as unreachable code.

No upstream HTTP calls are made. No data is served.

---

## Project status

- **Version**: 0.6.2 (deprecated · final)
- **Successor**: [`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/)
- **Source**: [github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea)
- **License**: MIT

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
