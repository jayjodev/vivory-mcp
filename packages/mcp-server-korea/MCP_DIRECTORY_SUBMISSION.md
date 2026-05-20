# MCP Directory Submission — `vivory-mcp-korea`

Distribution-layer runbook for the Korea MCP umbrella. Code/supply work is done — these are the registry submissions that turn `pip install`-able into discoverable.

**State (2026-05-20)**: **v0.5.0 ready locally** (PyPI 0.4.0 live; 0.5.0 publish pending tag push). 56 tools across 16 sources. `mcp-name` verification comment in README, `server.json` namespace `io.github.jayjodev/vivory-mcp-korea`. Ready for MCP Registry submission after v0.5.0 PyPI publish. Operator action remaining = tag push (mirror) → `mcp-publisher publish` → open the two awesome-mcp-servers PRs.

**Submission order (highest leverage first)**:
1. **Official MCP Registry** (registry.modelcontextprotocol.io) — anchor of the ecosystem, indexed by Smithery + Cursor + Glama
2. **punkpeye/awesome-mcp-servers** — ~86k stars, largest community list reach
3. **wong2/awesome-mcp-servers** — secondary community list
4. **Smithery.ai** — auto-detects from GitHub repo, no manual PR

Glama.ai crawls public GitHub MCP repos automatically — no submission needed.

---

## 0️⃣ Pre-flight: PyPI publish — DONE

`vivory-mcp-korea==0.4.0` is live on PyPI (verified 2026-05-20). README on PyPI carries the `<!-- mcp-name: io.github.jayjodev/vivory-mcp-korea -->` verification comment, and `server.json` namespace matches. No further publish action needed for this submission round.

For future version bumps, the release flow is documented in [`src/mcp-server-verification/PYPI_PUBLISH_WORKFLOW.md`](../mcp-server-verification/PYPI_PUBLISH_WORKFLOW.md) — same pattern: bump pyproject + `__init__.py` + `server.json`, push monorepo, then `git tag mcp-korea-v<X.Y.Z>` on the public mirror clone.

---

## 1️⃣ Official MCP Registry (registry.modelcontextprotocol.io) — **PRIMARY**

Anchor submission. Anthropic + GitHub + Microsoft + PulseMCP-backed. Once listed, downstream registries (Smithery, Cursor, Glama, mcp.so) auto-pick it up via the standardized REST API.

**Manifest**: `server.json` (lives at repo root, already committed).
**Namespace**: `io.github.jayjodev/vivory-mcp-korea` (GitHub-namespace = matches `jayjodev` GitHub user).
**Verification chain**: PyPI README contains `<!-- mcp-name: io.github.jayjodev/vivory-mcp-korea -->` → registry confirms ownership.

### Operator steps

```bash
# 1. Install mcp-publisher CLI (Homebrew or pre-built binary)
brew install mcp-publisher
# OR:
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" \
  | tar xz mcp-publisher && sudo mv mcp-publisher /usr/local/bin/

mcp-publisher --help  # confirm install

# 2. Authenticate via GitHub (OAuth device flow opens browser)
cd src/mcp-server-korea  # so server.json is in cwd
mcp-publisher login github

# 3. Publish (reads ./server.json, validates, submits)
mcp-publisher publish

# 4. Verify
curl -s https://registry.modelcontextprotocol.io/v0/servers \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print([s for s in d.get('servers',[]) if 'jayjodev' in s.get('name','')])"
```

**Expected lag**: instant. Listing visible at `https://registry.modelcontextprotocol.io/v0/servers/io.github.jayjodev/vivory-mcp-korea`.

**Updates**: bump version in `server.json` + `pyproject.toml`, re-publish PyPI, then `mcp-publisher publish` again.

---

## 2️⃣ punkpeye/awesome-mcp-servers — community list, primary reach

Repo: https://github.com/punkpeye/awesome-mcp-servers (~86.5k stars, ~10k forks, MIT)

**Section**: `Search & Data Extraction` (best fit per current taxonomy).

**PR title**:
```
Add vivory-mcp-korea (56 tools across 16 Korean public-data sources)
```

**Markdown line to add** (alphabetical within section):
```markdown
- [jayjodev/vivory-mcp-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea) 🐍 ☁️ 🏠 🇰🇷 - 55 tools across 15 official Korean public-data sources (KOSIS · BOK ECOS · DART · KMA · AirKorea · Opinet · HIRA · NMC · MOLIT · KTO · MFDS · MOIS · NEIS · Seoul OpenData · VWorld). Realtime ER beds, apartment transactions, KMA forecasts, gas-price rankings, KOSIS time-series, VWorld place/geocode + 1,534 museums & galleries — all normalized to English JSON with auto-attribution. No upstream API keys required. Install: `uvx vivory-mcp-korea`.
```

**PR body**:
```
## What this adds

`vivory-mcp-korea` — a single MCP server that bundles 55 tools spanning 15 official Korean government public-data APIs:

- KOSIS (Statistics Korea) — 15 tools
- BOK ECOS (Bank of Korea) — 1 tool
- DART (전자공시 · Financial Supervisory Service) — 6 tools (listed-company filings, financials, major shareholders)
- KMA (Korea Meteorological Administration) — 4 tools (weather + 6 living-weather indices)
- AirKorea (Ministry of Environment) — 2 tools
- Opinet (Korea National Oil Corporation) — 3 tools
- HIRA + NMC E-gen — 6 tools (healthcare directory + realtime emergency rooms)
- MOLIT (real estate transactions) — 4 tools
- KTO TourAPI — 4 tools
- MFDS (food nutrition) — 1 tool
- MOIS LOCALDATA (public restrooms) — 1 tool
- NEIS (K-12 schools) — 1 tool
- Seoul OpenData (parking, bike share) — 2 tools
- MoE EV chargers — 1 tool
- VWorld (국토교통부 공간정보) — 4 tools (place / address autocomplete, geocoder, 박물관·미술관 1,534 venue listing + detail)

## Why it's useful

Korean public-data APIs publish **only** in Korean, require per-source API key issuance, return JS-literal (not JSON) responses, and split similar data across 14+ portals. This MCP normalizes everything into English JSON, attributes the source per response, and presents one unified tool catalog the LLM can pick from.

For AI agents serving English-speaking users, journalists, analysts, or researchers needing Korean data, this is the first single entry point.

## Verification

- Repo: https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea
- PyPI: https://pypi.org/project/vivory-mcp-korea/
- Official MCP Registry: io.github.jayjodev/vivory-mcp-korea
- License: MIT (wrapper) / per-source upstream licenses (mostly KOGL Type 1, commercial-use OK)
- Backend: api.vivory.app/api/public-tools/* (anonymous tier 100/day per IP, no signup; pro 10k/day with VIVORY_API_KEY)

## Tool naming convention

Tools are namespaced by source for clean LLM picking:
`kosis_*` (15) · `kma_*` (4 incl. living weather) · `airkorea_*` (2) · `opinet_*` (3) · `hira_*` (3) · `nmc_*` (3) · `molit_*` (4) · `kto_*` (4) · `bok_*` (1) · `dart_*` (6) · `mfds_*` (1) · `mois_*` (1) · `neis_*` (1) · `seoul_*` + `ev_*` (3).

## Install one-liner

\`\`\`bash
claude mcp add vivory-korea -- uvx vivory-mcp-korea
\`\`\`

Or in `claude_desktop_config.json`:

\`\`\`json
{ "mcpServers": { "vivory-korea": { "command": "uvx", "args": ["vivory-mcp-korea"] } } }
\`\`\`
```

### Operator steps

```bash
# 1. Authenticate
gh auth login  # use GitHub web flow

# 2. Fork + clone
gh repo fork punkpeye/awesome-mcp-servers --clone --remote
cd awesome-mcp-servers

# 3. Find the "Search & Data Extraction" section, insert the line in alphabetical order
$EDITOR README.md

# 4. Commit + push + open PR
git checkout -b add-vivory-mcp-korea
git commit -am "Add vivory-mcp-korea (56 tools across 16 Korean public-data sources)"
git push -u origin add-vivory-mcp-korea
gh pr create --title "Add vivory-mcp-korea (56 tools across 16 Korean public-data sources)" \
  --body-file ../scripts/mcp_pr_body_punkpeye.md  # see scripts/mcp_registry_submit.sh
```

---

## 3️⃣ wong2/awesome-mcp-servers — secondary list

Repo: https://github.com/wong2/awesome-mcp-servers

Section: `Community Servers` (only third-party section currently; no geographic split).

**Markdown line**:
```markdown
- [vivory-mcp-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea) - Umbrella MCP for Korean public data — 56 tools across 16 sources (KOSIS · BOK · DART · KMA · AirKorea · Opinet · HIRA · NMC · MOLIT · KTO · MFDS · MOIS · NEIS · Seoul · VWorld). Realtime ER beds, apartment transactions, KMA forecasts, gas-price rankings, VWorld geocoder + 1,534 museums. No upstream API keys required.
```

Submit ~3 days after punkpeye/awesome PR lands cleanly (avoid double-spam appearance).

---

## 4️⃣ Smithery.ai — auto-detect from GitHub

Smithery's modern flow is: **publish to Official MCP Registry → Smithery auto-mirrors via API**. If the registry submission lands cleanly, no separate Smithery action is required.

If we want a hand-claimed listing earlier, the manual path is:

1. Visit https://smithery.ai/new
2. Sign in via GitHub
3. Paste `https://github.com/jayjodev/vivory-mcp` (with `packages/mcp-server-korea` subdirectory hint)
4. Select `stdio` transport
5. Smithery auto-generates a launcher config (`uvx vivory-mcp-korea`)
6. Hit Publish

Re-evaluate after registry listing has been live ≥48h to see if auto-mirror has happened.

---

## 5️⃣ Cursor MCP directory — auto via Smithery

Cursor's MCP directory pulls from Smithery + Official Registry. No separate submission needed.

---

## 6️⃣ Anthropic Connectors directory (claude.ai) — defer indefinitely

Gated marketplace requiring uptime SLA + verified org + security review. Re-evaluate only if api.vivory.app reaches Phase 3 ($5k MRR signal — see `project_revenue_path_calibration.md`).

---

## Submission checklist (before any registry action)

Run from `src/mcp-server-korea/`:

- [x] PyPI package `vivory-mcp-korea==0.4.0` published — `uvx vivory-mcp-korea` works
- [x] GitHub repo `jayjodev/vivory-mcp` is **public** with package directory at `packages/mcp-server-korea/`
- [x] README has `## Example prompts` (7 cross-source prompts incl. DART)
- [x] LICENSE file present (MIT)
- [x] Tool count and source list in README accurate (55 / 15 — added VWorld in v0.4)
- [x] `<!-- mcp-name: io.github.jayjodev/vivory-mcp-korea -->` HTML comment in README (verification anchor)
- [x] `server.json` at repo root with namespace `io.github.jayjodev/vivory-mcp-korea` (v0.5.0)
- [ ] **v0.5.0 published to PyPI** (waiting on tag push)
- [ ] **Registry listing live** (waiting on `mcp-publisher publish`)
- [ ] **punkpeye PR opened**
- [ ] **wong2 PR opened**

---

## Notes

- **Order matters**: registry → punkpeye → wong2. Registry is the canonical source of truth that downstream consumers (Smithery, Cursor, Glama) auto-mirror, so it should land first.
- 🇰🇷 flag emoji in punkpeye line signals geography clearly.
- Earlier draft `mcp-server-kosis/MCP_DIRECTORY_SUBMISSION.md` is now superseded; the umbrella supersedes the standalone. KOSIS package is EOL 2026-12-31 (final maintenance release 0.1.2).
- **Sister `vivory-mcp-verification`** is **v0.5.0 ready locally** (PyPI 0.4.1 live; 0.5.0 publish pending) — 53 tools / 22 categories. Together = **109 tools, one unified Pro key**. See [`src/mcp-server-verification/MCP_DIRECTORY_SUBMISSION.md`](../mcp-server-verification/MCP_DIRECTORY_SUBMISSION.md) — submit both packets in the same wave.
- After all three (registry + 2 community lists) land: discovery via Google "Korea MCP server", "Korean public data API", "MOLIT real estate AI agent" should surface within 2–4 weeks.
