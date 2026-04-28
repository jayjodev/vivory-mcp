# Vivory MCP Servers

**Korean public-data MCP servers for AI agents** — KOSIS Statistics Korea (live), BoK ECOS · NEIS · LOCALDATA (planned).

Built and maintained by **[Vivory](https://vivory.app)**. Backend powered by the [Vivory Korea Data Gateway](https://api.vivory.app).

[![PyPI - Version](https://img.shields.io/pypi/v/vivory-mcp-kosis.svg)](https://pypi.org/project/vivory-mcp-kosis/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why

Korean public statistics (population, GDP, CPI, employment, trade, etc.) are published by official agencies via Korean-only APIs that require local accounts and return JS-literal responses with mixed taxonomies. This repo packages them as [Model Context Protocol](https://modelcontextprotocol.io) servers so any MCP-compatible client (Claude Desktop, Claude Code, etc.) can query Korean data in English with zero setup.

```
Foreign user → Claude → vivory-mcp-* → api.vivory.app → kosis.kr / ecos.bok.or.kr / etc.
                                       (caching, attribution, normalization)
```

No KOSIS account, no API key, no Korean phone — just install and ask.

---

## Packages

This is a monorepo of MCP server packages. Each is independently installable from PyPI.

| Package | Status | Tools | Source |
|---|---|---|---|
| **[`vivory-mcp-kosis`](packages/mcp-server-kosis)** | Live | 15 | KOSIS — Statistics Korea curated key indicators |
| **[`vivory-mcp-korea`](packages/mcp-server-korea)** | Live (KOSIS only) | 15 | Umbrella — adds BoK ECOS, NEIS, LOCALDATA, etc. as v0.2+ |

### Recommended:

- **One source only** → install the dedicated package (`vivory-mcp-kosis`)
- **All Korean data** → install the umbrella (`vivory-mcp-korea`) — auto-grows as we add sources

---

## Quick install (Claude Desktop)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

Or to use the umbrella (all Korean data):

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

Restart Claude Desktop. The tools appear in the tool palette.

> **PyPI release pending** — until then use:
> ```
> uvx --from "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-kosis" vivory-mcp-kosis
> ```

---

## Example prompts

Ask Claude (or any MCP client):

> *"What's Korea's CPI trend over the last 24 months?"*
> *"Show me Korean quarterly GDP growth, last 12 quarters."*
> *"Search KOSIS for tables related to youth unemployment."*
> *"What's the indicator ID for 추계인구?"*

Claude picks the right tool automatically.

---

## Architecture

```
packages/
├── mcp-server-kosis/          # KOSIS standalone MCP server
│   ├── src/vivory_mcp_kosis/
│   │   ├── server.py          # 15 KOSIS tool definitions
│   │   └── client.py          # HTTP wrapper to api.vivory.app
│   ├── pyproject.toml
│   └── README.md
│
└── mcp-server-korea/          # Umbrella MCP server
    ├── src/vivory_mcp_korea/
    │   ├── server.py          # Aggregates tools from all sources
    │   ├── client.py
    │   └── tools/
    │       ├── kosis.py       # KOSIS tool catalog
    │       └── (ecos.py, neis.py, etc. — planned)
    └── ...
```

All packages are **thin wrappers** — no API keys, no rate limit handling, no parsing logic. They translate MCP tool calls → HTTP GETs against [api.vivory.app](https://api.vivory.app), where the heavy lifting lives.

---

## Self-hosting

Set `VIVORY_API_BASE` to point at your own backend:

```bash
export VIVORY_API_BASE="http://localhost:8000/api"
```

The Vivory backend code is **not** in this repo (it lives in the private Vivory app monorepo). If you want to run the full stack, you'll need to implement the `/api/public-tools/kosis/*` endpoints yourself or contact us about licensing.

---

## License

- **MCP wrapper code** (this repo): MIT
- **KOSIS data**: 공공누리(KOGL) Type 1 — commercial use permitted with attribution
- **Other sources**: per-source license (see each package's README)

Every tool response includes an `attribution` block. When citing or redistributing data, include the `attribution_required` text.

---

## Contributing

Issues and PRs welcome. Specifically interested in:

- Adding more Korean public data sources to the umbrella
- Improving tool descriptions for better LLM tool-use accuracy
- Adapting for other MCP clients beyond Claude

---

## Project status

- **Repo source of truth**: this repo (`vivory-mcp`) — packages here mirror what's published to PyPI
- **Vivory backend**: private (api.vivory.app)
- **Issues / discussions**: [github.com/jayjodev/vivory-mcp/issues](https://github.com/jayjodev/vivory-mcp/issues)

---

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
