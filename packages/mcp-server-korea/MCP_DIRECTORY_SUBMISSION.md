# MCP Directory Submission Drafts — `vivory-mcp-korea` (umbrella)

Ready-to-submit entries for community MCP server directories. The umbrella package supersedes the standalone `vivory-mcp-kosis` for first submissions because the broader scope (13 sources, 45 tools) clears reviewer "is this useful?" bars more easily.

Submit list 1 first; if it lands cleanly, submit list 2 ~3 days later.

---

## 1️⃣ punkpeye/awesome-mcp-servers — primary target

Repo: https://github.com/punkpeye/awesome-mcp-servers

**Section**: 🔎 **Search & Data Extraction** (best fit) or 📊 **Data Platforms** (secondary).

**PR title**:
```
Add vivory-mcp-korea (umbrella MCP for 13 Korean public-data sources)
```

**Markdown line to add** (alphabetically sorted in section):
```markdown
- [jayjodev/vivory-mcp-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea) 🐍 ☁️ 🏠 🇰🇷 - 45 tools across 13 official Korean public-data sources (KOSIS · BOK · KMA · AirKorea · Opinet · HIRA · NMC · MOLIT · KTO · MFDS · MOIS · NEIS · Seoul). Realtime ER beds, apartment transactions, KMA forecasts, gas-price rankings, KOSIS time-series — all normalized to English JSON with auto-attribution. No upstream API keys required. Install: `uvx vivory-mcp-korea`. Ask Claude: *"Where are ER beds available near Gangnam right now?"*
```

**PR body**:
```
## What this adds

`vivory-mcp-korea` — a single MCP server that bundles 45 tools spanning
13 official Korean government public-data APIs:

- KOSIS (Statistics Korea)
- BOK ECOS (Bank of Korea)
- KMA (Korea Meteorological Administration) — weather + 6 living-weather indices
- AirKorea (Ministry of Environment)
- Opinet (Korea National Oil Corporation)
- HIRA + NMC (healthcare directory + realtime emergency rooms)
- MOLIT (real estate transactions)
- KTO TourAPI
- MFDS (food nutrition)
- MOIS LOCALDATA (public restrooms)
- NEIS (K-12 schools)
- Seoul OpenData (parking, bike share)

## Why it's useful

Korean public-data APIs publish **only** in Korean, require per-source
API key issuance, return JS-literal (not JSON) responses, and split
similar data across 14+ portals. This MCP normalizes everything into
English JSON, attributes the source per response, and presents one
unified tool catalog the LLM can pick from.

For AI agents serving English-speaking users, journalists, analysts, or
researchers needing Korean data, this is the first single entry point.

## Verification

- Repo: https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea
- License: MIT (wrapper) / per-source upstream licenses (mostly KOGL Type 1, commercial-use OK)
- Backend: api.vivory.app/api/public-tools/* (anonymous tier 100/day per IP, no signup; pro 10k/day with VIVORY_API_KEY)
- Tools count by source listed in README.md

## Tool naming convention

Tools are namespaced by source for clean LLM picking:
`kosis_*` (15) · `kma_*` (4 incl. living weather) · `airkorea_*` (2) ·
`opinet_*` (3) · `hira_*` (3) · `nmc_*` (3) · `molit_*` (4) · `kto_*` (4) ·
`bok_*` (1) · `mfds_*` (1) · `mois_*` (1) · `neis_*` (1) · `seoul_*` + `ev_*` (3).

## Install one-liner

```bash
claude mcp add vivory-korea -- uvx vivory-mcp-korea
```

Or in `claude_desktop_config.json`:

```json
{ "mcpServers": { "vivory-korea": { "command": "uvx", "args": ["vivory-mcp-korea"] } } }
```

PyPI: https://pypi.org/project/vivory-mcp-korea/
```

---

## 2️⃣ wong2/awesome-mcp-servers — secondary target

Repo: https://github.com/wong2/awesome-mcp-servers

**Section**: "Government Data" / "Public Data" / generic "Data" — fall back to "Other" if none.

**Markdown line**:
```markdown
- [vivory-mcp-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea) - Umbrella MCP for Korean public data — 45 tools across 13 sources (KOSIS · BOK · KMA · AirKorea · Opinet · HIRA · NMC · MOLIT · KTO · MFDS · MOIS · NEIS · Seoul). Realtime ER beds, apartment transactions, KMA forecasts, gas-price rankings. No upstream API keys required.
```

---

## 3️⃣ Anthropic official `modelcontextprotocol/servers` — defer

Curated. Submission bar: PyPI release + ecosystem traction (≥100 stars,
external mention, demonstrated reliability).

**Defer until v0.3+** (after PyPI publish + at least one of the lists above lands).

---

## 4️⃣ Anthropic Connectors directory (claude.ai) — defer indefinitely

Gated marketplace requiring uptime SLA + verified org + security review.
Community lists deliver 90% of discovery. Re-evaluate only if
api.vivory.app reaches Phase 3 ($5k MRR signal — see `project_revenue_path_calibration.md`).

---

## Submission checklist (before any PR)

- [x] PyPI package `vivory-mcp-korea==0.2.0` published — `uvx vivory-mcp-korea` works
- [x] GitHub repo `jayjodev/vivory-mcp` is **public** with package directory at `packages/mcp-server-korea/`
- [x] README has `## Example prompts` (7 cross-source prompts)
- [x] LICENSE file present (MIT)
- [x] Self-test: fresh `pip install vivory-mcp-korea` reports tools=45, handlers=45, parity=True
- [x] Tool count and source list in README accurate (45 / 13)

---

## Notes

- Submit **list 1 (punkpeye)** first — largest reach (~70k stars), fastest review.
- Submit **list 2 (wong2)** ~3 days later if list 1 lands cleanly.
- Both are GitHub PRs, free of cost.
- The 🇰🇷 flag emoji in list 1 signals geography clearly.
- Earlier draft `mcp-server-kosis/MCP_DIRECTORY_SUBMISSION.md` is now superseded; the umbrella is the better submission target. Keep it as historical record only.

After both land: discovery via Google "Korea MCP server", "Korean public data
API", "MOLIT real estate AI agent" should surface within 2–4 weeks.
