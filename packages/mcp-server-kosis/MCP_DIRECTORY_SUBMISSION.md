# MCP Directory Submission Drafts (HISTORICAL — superseded by umbrella)

> **⚠ Superseded 2026-05-06**: First-submission target is now the umbrella package `vivory-mcp-korea` (13 sources / 45 tools), not this kosis-only one. See [`mcp-server-korea/MCP_DIRECTORY_SUBMISSION.md`](../mcp-server-korea/MCP_DIRECTORY_SUBMISSION.md) for current punkpeye/wong2 PR drafts. This document remains as historical record only — submit the umbrella first; consider this kosis-only submission only if directories explicitly want narrower-scope listings.

Ready-to-submit entries for community MCP server directories. Pick one or multiple to maximize discovery.

---

## 1️⃣ punkpeye/awesome-mcp-servers (largest community list)

Repo: https://github.com/punkpeye/awesome-mcp-servers

**Section**: 🔎 **Search & Data Extraction** (best fit) or 📊 **Data Platforms** (secondary)

**PR title**:
```
Add vivory-mcp-kosis (KOSIS Statistics Korea — Korean public statistics)
```

**Markdown line to add** (alphabetically sorted in section):
```markdown
- [jayjodev/vivory-mcp-kosis](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis) 🐍 ☁️ 🏠 🇰🇷 - KOSIS (Statistics Korea) — Korean macro/social/economic statistics for AI agents. 16 curated indicator categories (Population, Labor, CPI, GDP, Trade, etc.) + full catalog search + time-series. No KOSIS account required. Install: `uvx --from "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-kosis" vivory-mcp-kosis`. Ask Claude: "What's Korea's CPI trend over 24 months?"
```

**PR body**:
```
## What this adds

`vivory-mcp-kosis` — an MCP server exposing 15 tools that wrap KOSIS
(Statistics Korea, https://kosis.kr), the official Korean government
statistics portal. Lets foreign analysts, AI agents, and developers
query Korean macro/social/economic data in English.

## Why it's useful

- Korean public statistics are published in Korean only with API keys
  and JS-literal responses. This MCP normalizes everything to English
  with attribution-compliant JSON.
- 16 curated key indicator categories (Population, Labor, CPI, GDP,
  Trade Balance, Household Income, etc.) work without any KOSIS account
  or 활용분야 (subscription field) registration.
- KOSIS data is licensed KOGL Type 1 — commercial use permitted with
  attribution (auto-injected by the server).

## Verification

- Repo: https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis
- Install: see README
- License: MIT (wrapper) / KOGL Type 1 (KOSIS data)
- Backend gateway: https://api.vivory.app/api/public-tools/kosis/

## Tools (15)

Discovery: kosis_categories, kosis_category_indicators,
kosis_indicators_search, kosis_indicator_timeseries, kosis_table_search.
Pre-built: kosis_population, kosis_gdp, kosis_employment, kosis_cpi,
kosis_household_income, kosis_trade_balance.
Meta: kosis_table_meta, kosis_table_explanation, kosis_statistic_tree.
Aggregate: kosis_key_indicators.
```

---

## 2️⃣ wong2/awesome-mcp-servers (second-largest community list)

Repo: https://github.com/wong2/awesome-mcp-servers

**Section**: Look for "Government Data", "Public Data", or "Data" — fall back to a generic "Other" or "Productivity" if none.

**Markdown line**:
```markdown
- [vivory-mcp-kosis](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-kosis) - KOSIS (Statistics Korea) — Korean public statistics for AI agents. 16 indicator categories + full catalog search + time-series. No KOSIS account required.
```

---

## 3️⃣ Anthropic official `modelcontextprotocol/servers` (selective)

Repo: https://github.com/modelcontextprotocol/servers

This repo is curated and accepts only a small number of high-quality community servers. Submission is best done **after PyPI release + 100+ stars** to clear the bar.

**Path**: README.md → "📚 Resources" or "Community Servers" section (if exists at submission time).

**Defer to v0.2+** once the project has ecosystem proof points.

---

## 4️⃣ Anthropic Connectors directory (claude.ai)

Anthropic operates a managed Connectors marketplace at https://claude.ai. Submission is gated and requires:
- Production-grade reliability (uptime SLA)
- Verified org/identity
- Security review

**Defer indefinitely** — community lists (1, 2) deliver 90% of discovery.

---

## Submission checklist (before any PR)

- [ ] PyPI package published — install one-liner works for users
- [ ] README has at least one `## Example prompts` section
- [ ] Repo has a star count >= 5 (avoids spam reject)
- [ ] LICENSE file present (MIT for wrapper)
- [ ] Tools count and capabilities accurately documented
- [ ] Self-test: `uvx vivory-mcp-kosis` runs without errors

---

## Notes

- Submit **list 1 (punkpeye)** first — largest reach, fastest review.
- Submit **list 2 (wong2)** ~3 days later if list 1 lands cleanly.
- Both are GitHub PRs, free of cost.
- Korean flag (🇰🇷) emoji is optional but signals geography clearly.

After both lands: discovery via Google search "Korea MCP server", "KOSIS API",
"Korean statistics AI agent" should surface the package within 2–4 weeks.
