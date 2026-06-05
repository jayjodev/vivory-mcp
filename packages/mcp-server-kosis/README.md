# vivory-mcp-kosis — ⚠️ DEPRECATED v0.1.4

> **This package is deprecated.** Both `vivory-mcp-kosis` AND the intermediate `vivory-mcp-korea` umbrella are retired. Migrate directly to **[`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/)** — Korean verdict tools are bundled there, and the Tools Pro $4.99/mo key (bundle absorb 2026-06-01, single paid tier) authenticates the catalog.
>
> **Migrate in one line:**
>
> ```bash
> uvx vivory-mcp-verification
> ```
>
> The upstream KOSIS gateway at `api.vivory.app/api/public-tools/kosis/*` went cluster-internal on 2026-05-22. Old KOSIS tool calls from external networks return 404 regardless of this MCP layer — that is why this release ships as deprecation-only.

---

## Why deprecated

Korean public-data raw access (KOSIS, BOK, DART, KMA, MOLIT, VWorld, NEIS, etc.) was retired because raw wrappers **redistributed data rather than verified it** — conflicting with Vivory's verifiable-AI-work mission and the source ToS of several upstream providers.

Korean public sources are still used inside Vivory — as **underlying evidence for verdicts** in `vivory-mcp-verification`:

| Verdict tool (in vivory-mcp-verification) | Korean source used as evidence |
|---|---|
| `kor_law_currency` | 법령정보센터 (law.go.kr) |
| `kor_company_status` | NTS 사업자등록 + CSL cross-check |
| `doi_retraction_status` | Crossref + OpenAlex + PubPeer |

---

## Migration

Update your `claude_desktop_config.json` (or `claude mcp add` invocation) from this:

```json
{
  "mcpServers": {
    "vivory-kosis": {
      "command": "uvx",
      "args": ["vivory-mcp-kosis"]
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

To give existing v0.1.x users a clear migration signal, the package:

- Ships exactly **one tool** (`vivory_kosis_deprecated_migration_notice`) that returns the migration payload.
- Returns the **same deprecation payload** for any other tool name the LLM tries (including the old `kosis_categories`, `kosis_gdp`, `kosis_cpi`, etc.) instead of silently 404ing.
- Prints a loud stderr banner on startup (suppress with `VIVORY_MCP_QUIET=1`).

No upstream HTTP calls are made. No data is served.

---

## Project status

- **Version**: 0.1.4 (deprecated · final)
- **Successor**: [`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/)
- **Source**: [github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis)
- **License**: MIT

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
