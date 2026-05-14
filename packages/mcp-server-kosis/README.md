# vivory-mcp-kosis — ⚠️ DEPRECATED

> **This package is deprecated.** All KOSIS tools (and 13 additional Korean public-data sources, 51 tools total) are now bundled in [`vivory-mcp-korea`](https://pypi.org/project/vivory-mcp-korea/) — the umbrella replacement.
>
> **Migrate**: `pip uninstall vivory-mcp-kosis && pip install vivory-mcp-korea` (or `uvx vivory-mcp-korea`). Tool names are unchanged.
>
> No further updates will ship to this package. Last release: 0.1.1 (2026-05-07, deprecation marker).

---

MCP server for **KOSIS (Statistics Korea)** — Korean macro/social/economic statistics for AI agents.

This package wraps the [Vivory Korea Data Gateway](https://api.vivory.app/api/public-tools/kosis) and exposes 15 tools to any [MCP](https://modelcontextprotocol.io)-compatible client (Claude Desktop, Claude Code, etc.).

Built and maintained by **[Vivory](https://vivory.app)**. Data sourced from **[KOSIS · 통계청](https://kosis.kr)**.

> **Need more than KOSIS?** [`vivory-mcp-korea`](https://pypi.org/project/vivory-mcp-korea/) is the umbrella package — 51 tools across 14 sources (KOSIS · BOK · DART · KMA · AirKorea · Opinet · HIRA · NMC · MOLIT · KTO · MFDS · MOIS · NEIS · Seoul OpenData). Use this standalone package only if you want a smaller install scoped to KOSIS alone.

---

## Why

Korean public statistics (GDP, CPI, unemployment, demographics, trade balance, etc.) are published by Statistics Korea via [KOSIS](https://kosis.kr) — but the API is Korean-only, requires a key, returns JS-literal responses, and uses scattered taxonomies. This MCP server lets foreign analysts, AI agents, and developers query Korean statistics in English without any setup beyond a one-line install.

```
You → Claude → vivory-mcp-kosis → api.vivory.app → kosis.kr
                                  (caching, attribution, normalization)
```

No KOSIS account, no API key, no Korean phone — just install and ask.

---

## Installation

> **Note**: PyPI publication coming soon. Until then, install directly from this repo via Git.

### Option A — Claude Desktop (recommended)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "vivory-kosis": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-kosis",
        "vivory-mcp-kosis"
      ]
    }
  }
}
```

Restart Claude Desktop. The 15 KOSIS tools appear in the tool palette.

### Option B — Claude Code (CLI)

```bash
claude mcp add vivory-kosis -- uvx --from "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-kosis" vivory-mcp-kosis
```

### Option C — Manual pip install (from Git)

```bash
pip install "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-kosis"
vivory-mcp-kosis  # runs the stdio MCP server
```

### Option D — Once published to PyPI (planned)

```bash
pip install vivory-mcp-kosis           # or:
uvx vivory-mcp-kosis                    # zero-install run
```

---

## Tools

### Discovery (subscription-free)

| Tool | Purpose |
|---|---|
| `kosis_categories` | List 16 ROOT categories (Population, Labor, CPI, GDP, etc.) |
| `kosis_category_indicators` | List indicators inside a category (returns `indicator_id` for time-series) |
| `kosis_indicators_search` | Search indicators by Korean keyword |
| `kosis_indicator_timeseries` | Fetch time-series values by `indicator_id` or `indicator_name` |
| `kosis_table_search` | Full-text search across the entire KOSIS catalog |

### Pre-built indicators

| Tool | Indicator |
|---|---|
| `kosis_population` | Total population by region (annual) |
| `kosis_gdp` | National accounts main indicators (quarterly) |
| `kosis_employment` | Unemployment, employment, participation (monthly) |
| `kosis_cpi` | Consumer Price Index — overall, food, core (monthly) |
| `kosis_household_income` | Household Income & Expenditure by decile (quarterly) |
| `kosis_trade_balance` | Exports, imports, net exports (monthly) |

### Meta

| Tool | Purpose |
|---|---|
| `kosis_table_meta` | Table metadata (TBL/ORG/PRD/ITM/CMMT/UNIT/SOURCE/WGT/NCD) |
| `kosis_table_explanation` | Survey methodology, legal basis, periodicity |
| `kosis_statistic_tree` | Browse the hierarchical statistic tree |

### Aggregate

| Tool | Purpose |
|---|---|
| `kosis_key_indicators` | Snapshot of 6 key indicators in one call |

---

## Example prompts to Claude

After installing the MCP server, just ask Claude:

> *"What's Korea's population trend over the last 10 years?"*
> *"How has the Korean Consumer Price Index moved over the last 24 months?"*
> *"Show me Korean quarterly GDP growth, last 12 quarters."*
> *"Search KOSIS for tables related to youth unemployment."*
> *"What's the indicator ID for 추계인구?"*

Claude will pick the right tool automatically.

---

## Data attribution

Every tool response includes an `attribution` block:

```json
{
  "attribution": {
    "source": "KOSIS",
    "agency": "통계청 (Statistics Korea)",
    "agency_en": "Statistics Korea (KOSTAT)",
    "license": "Public data — commercial use allowed with attribution",
    "source_url": "https://kosis.kr",
    "attribution_required": "자료: KOSIS 국가통계포털, 통계청"
  }
}
```

When citing or redistributing data, include the `attribution_required` text. KOSIS data is licensed under [공공누리(KOGL) Type 1](https://www.kogl.or.kr/info/license.do) — commercial use, modification, and redistribution permitted with source attribution.

---

## Self-hosting

By default the server calls `https://api.vivory.app/api`. To point at your own Vivory deployment (or local development), set:

```bash
export VIVORY_API_BASE="http://localhost:8000/api"
```

You'll also need a working Vivory backend with `KOSIS_API_KEY` configured — see Vivory backend (private monorepo).

---

## Rate limits

The Vivory gateway caches all KOSIS responses in Redis (TTL 1h~24h depending on endpoint), so individual MCP calls are typically sub-50ms. Upstream KOSIS limits are 1,000 calls/minute and 40,000 cells per response — Vivory caching hides these almost entirely from you.

For high-volume commercial use, contact [contact@vivory.app](mailto:contact@vivory.app) about Pro tier ($29/mo) and Enterprise tier ($299/mo).

---

## Project status

- **Version**: 0.1.0
- **Stability**: Beta — API surface stable, may add tools without breaking changes
- **Source**: [github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis)
- **Issues**: [github.com/jayjodev/vivory-mcp/issues](https://github.com/jayjodev/vivory-mcp/issues)
- **License**: MIT (this MCP wrapper). Underlying KOSIS data: KOGL Type 1.

---

## What's next

- More public Korean datasets (BoK ECOS, NEIS schools, real estate, weather, air quality) under separate MCP servers
- Anthropic MCP Directory submission
- `vivory-mcp-korea` umbrella package combining all Korean data sources

---

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
