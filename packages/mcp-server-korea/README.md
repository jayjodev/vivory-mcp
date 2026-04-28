# vivory-mcp-korea

Umbrella MCP server bundling **all Korean public-data sources** into a single registration. Install once, get every Vivory-supported Korean dataset.

Powered by the [Vivory Korea Data Gateway](https://api.vivory.app) — all backend auth, caching, attribution, and normalization handled upstream.

---

## What's included

### v0.1 — KOSIS only (15 tools)

[Statistics Korea, 통계청 국가통계포털](https://kosis.kr) — 16 categories of curated key indicators (Population, Labor, CPI, GDP, Trade Balance, Household Income, etc.) + full catalog search + time-series.

### Planned for v0.2+

- **BoK ECOS** (한국은행 경제통계시스템) — interest rates, exchange rates, monetary aggregates
- **NEIS** (교육부 나이스) — 11,900+ Korean schools (info / class size / meals / academic calendar)
- **LOCALDATA** (행정안전부) — businesses by category × region
- **Air Korea** — real-time PM2.5 / PM10 / O3 by 17 provinces
- **KMA** (기상청) — short-term weather forecasts for 20 cities
- **Opinet** — gas station prices nationwide
- **HIRA** — hospitals · pharmacies · ER status
- **DART** (전자공시) — Korean listed companies' filings/financials/shareholders

When v0.2+ ships, **users don't need to re-install** — `vivory-mcp-korea` auto-includes new tools as they're added upstream. Single registration command, ever-growing toolbox.

---

## Why this exists

Two installation patterns serve different audiences:

| Use case | Recommended package |
|---|---|
| Just KOSIS statistics | [`vivory-mcp-kosis`](../mcp-server-kosis) — narrower scope, smaller install |
| All Korean public data | **`vivory-mcp-korea`** ← this package |

If you only need one source, install that source's standalone package. If you want everything Korea-related, install this umbrella.

---

## Installation

> **Note**: PyPI publication coming soon. Until then, install from this repo via Git.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "vivory-korea": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-korea",
        "vivory-mcp-korea"
      ]
    }
  }
}
```

Restart Claude Desktop. All Korean data tools appear in the tool palette.

### Claude Code

```bash
claude mcp add vivory-korea -- uvx --from "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-korea" vivory-mcp-korea
```

### pip from Git

```bash
pip install "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-korea"
vivory-mcp-korea  # runs the stdio MCP server
```

### Once on PyPI (planned)

```bash
uvx vivory-mcp-korea
```

---

## Self-hosting

```bash
export VIVORY_API_BASE="http://localhost:8000/api"
```

Requires a working Vivory backend with `KOSIS_API_KEY` configured — see the parent repo at [github.com/jayjodev/vivory](https://github.com/jayjodev/vivory).

---

## Example prompts

> *"What's Korea's CPI trend over the last 24 months?"*
> *"Compare Korean and Japanese unemployment trends... actually start by giving me Korea's data first."*
> *"Search KOSIS for tables related to youth employment, then show me the latest data."*

Claude picks the right tool automatically.

---

## Data attribution

Every response includes an `attribution` block per source. KOSIS data is licensed [공공누리(KOGL) Type 1](https://www.kogl.or.kr/info/license.do) — commercial use permitted with source attribution.

---

## Project status

- **Version**: 0.1.0 (KOSIS only)
- **Source**: [github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea)
- **License**: MIT (wrapper) / per-source license for upstream data
- **Roadmap**: see "Planned for v0.2+" above

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
