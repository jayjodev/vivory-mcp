# vivory-mcp-korea

<!-- mcp-name: io.github.jayjodev/vivory-mcp-korea -->

**Umbrella MCP server bundling Korean public-data sources into a single installation.** 55 tools across 15 official Korean government APIs — install once, get every Vivory-supported Korean dataset.

Powered by the [Vivory Korea Data Gateway](https://api.vivory.app) — backend handles auth, caching, attribution, JS-literal parsing, and rate-limit gating.

---

## What's included

### v0.4 — 15 sources, 55 tools

| Source | Tools | What it covers |
|---|---|---|
| **KOSIS** (통계청) | 15 | Macro/social/economic statistics — Population, Labor, CPI, GDP, Trade Balance, Household Income + full catalog search + time-series. |
| **BOK** (한국은행 ECOS) | 1 | Macro dashboard — base rate, CPI, unemployment, M2, KRW/USD, recent series. |
| **DART** (전자공시 · 금감원) | 6 | Korean listed-company filings, financial statements, major shareholders, company-info lookup, daily disclosures feed. |
| **KMA** (기상청) | 4 | Real-time observation, short-range forecast, city presets, six living-weather indices (UV / sensible temp / pollen / etc.). |
| **AirKorea** (환경부) | 2 | Real-time PM10 / PM2.5 / O3 / NO2 / SO2 / CO per station, plus regional forecast. |
| **Opinet** (한국석유공사) | 3 | National avg / per-SIDO / Top-10 cheapest gas stations (5 fuel grades). |
| **HIRA** (건강보험심사평가원) | 3 | Hospital + pharmacy directory search, hospitals nearby a coordinate. |
| **NMC** (국립중앙의료원 E-gen) | 3 | ER real-time bed availability, night-shift pharmacies, trauma centers. |
| **MOLIT** (국토교통부) | 4 | Apartment sale / rent transactions (RTMS), price trend, LAWD region codes. |
| **KTO** (한국관광공사 TourAPI) | 4 | Tour spots by region, festivals by date, nearby tour by coordinate, full detail. |
| **MFDS** (식품의약품안전처) | 1 | Korean food nutrition database — calories, macros, vitamins, minerals. |
| **MOIS LOCALDATA** (행정안전부) | 1 | ~50,000 public restrooms by address. |
| **NEIS** (교육부 나이스) | 1 | K-12 school search across 12,555 schools. |
| **Seoul OpenData** (서울시) | 2 | Public parking lots (~2,300 with realtime), Seoul Bike (따릉이) stations. |
| **MoE EV** (환경부) | 1 | EV chargers per SIDO with realtime status. |
| **VWorld** (국토교통부 공간정보) | 4 | Place / address autocomplete, geocoder (address → WGS84), 박물관·미술관 1,534 venue listing + detail (Wikipedia + Google Places enrichment). |

Tools are namespaced by source (`kosis_*`, `kma_*`, `dart_*`, `hira_*`, …) so Claude can pick the right one automatically.

> **DART note**: `dart_company_search` resolves once the corp_code mapping has been synced upstream. The Vivory backend now auto-refreshes the ~3,500 listed-company mapping on a monthly cron (every 1st 05:10 KST); operators can still trigger an on-demand sync via `POST /api/public-tools/dart/admin/sync-corp-codes` (admin auth) if needed. Status visible via `dart_meta`. Other DART tools (disclosures, financials, major-shareholders) work directly when you already have an 8-digit `corp_code`.

### Coming next (v0.5+)

- **Forest Service** — hiking trails, mountain points.
- **Kakao Local** reverse geocoding.
- **AED** locations (NMC E-gen — pending data.go.kr activation).
- **University search** (KCUE — pending data.go.kr activation).
- **MVNO plans** (Korea Post — pending data.go.kr activation).
- **VWorld v2** — full LOCALDATA venue surface beyond museums (restaurant / cafe / cinema / gym / etc.).

When these ship, **users don't need to re-install** — `vivory-mcp-korea` auto-includes new tools as they're wired upstream.

---

## Why this exists

Korean public-data APIs publish exclusively in Korean, require per-API key issuance, return JS-literal (not JSON) responses, and split similar data across 14+ portals. This MCP server normalizes everything to English JSON, attributes data per response, and presents one tool catalog the LLM can navigate.

| Use case | Recommended package |
|---|---|
| All Korean public data | **`vivory-mcp-korea`** ← this package |
| Verification (DOI · archive · provenance · peer review · forecast) | `vivory-mcp-verification` — sister umbrella scaffold, 21 tools (PyPI ship pending) |

> The earlier `vivory-mcp-kosis` standalone has been deprecated; all KOSIS tools ship inside this umbrella.

---

## Installation

Live on PyPI as [`vivory-mcp-korea`](https://pypi.org/project/vivory-mcp-korea/).

### Claude Code

```bash
claude mcp add vivory-korea -- uvx vivory-mcp-korea
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

Restart Claude Desktop. All 51 Korean data tools appear in the tool palette.

### pip / pipx

```bash
pip install vivory-mcp-korea
vivory-mcp-korea  # runs the stdio MCP server
```

### Install from source (development)

```bash
pip install "git+https://github.com/jayjodev/vivory-mcp.git#subdirectory=packages/mcp-server-korea"
```

---

## API tier — Vivory API Pro

The server runs anonymously by default — **100 calls/day per IP**, no signup. Works for casual use.

For higher limits, sign up at **[api.vivory.app/dashboard/public-api](https://api.vivory.app/dashboard/public-api)** and set `VIVORY_API_KEY`. **One key unlocks both MCPs**: a Pro key for `vivory-mcp-korea` also unlocks the sibling [`vivory-mcp-verification`](https://pypi.org/project/vivory-mcp-verification/) (45 verification tools across 18 clusters — DOI / Wayback / SEC EDGAR / GLEIF / Wikidata / ClinicalTrials / World Bank / USPTO / OSM / DefiLlama / USGS / MOLIT realestate, etc.).

| Tier | Daily limit | How to enable |
|---|---|---|
| Anonymous | 100/day per IP | Default — no setup |
| Pro | 10,000/day shared across 100+ tools | $29/mo USDC (CoolWallet · Arbitrum) or card. 31-day pass, no auto-renew, no custody. `VIVORY_API_KEY=…` env var. |
| Enterprise | 100,000/day | Contact contact@vivory.app (self-serve only, no SaaS sales) |

```json
{
  "mcpServers": {
    "vivory-korea": {
      "command": "uvx",
      "args": ["vivory-mcp-korea"],
      "env": {
        "VIVORY_API_KEY": "vk_live_..."
      }
    }
  }
}
```

---

## Self-hosting

```bash
export VIVORY_API_BASE="http://localhost:8000/api"
```

Requires a working Vivory backend with upstream API keys configured (KOSIS / KMA / MOLIT / Opinet / etc.) — see Vivory backend (private monorepo).

---

## Example prompts

> *"What's Korea's CPI trend over the last 24 months?"*
> *"What's the air quality in Seoul right now, and forecast for tomorrow?"*
> *"Find the 5 cheapest diesel stations near Incheon airport."*
> *"List trauma-center-equipped hospitals within 10 km of latitude 37.5, longitude 127.0."*
> *"Show me Gangnam-gu apartment sale transactions in April 2026."*
> *"What festivals are happening in Seoul between May 1 and May 15?"*
> *"How many bikes are currently available at Seoul Bike stations in Mapo-gu?"*

Claude picks the right tool automatically from the 51-tool catalog.

For Korean listed-company queries (DART):

> *"What did Samsung Electronics report in its 2024 annual filing — find their corp_code first."* → `dart_company_search` → `dart_financials`
> *"Show me all KOSPI disclosures filed today."* → `dart_disclosures`
> *"Who are the major shareholders of Hyundai Motor in 2024?"* → `dart_company_search` → `dart_major_shareholders`

---

## Data attribution

Every response includes an `attribution` block — source, license, citation requirement.

| Source | License | Commercial use |
|---|---|---|
| KOSIS / KOGL Type 1 | Open with attribution | ✅ |
| BOK ECOS / KOGL Type 1 | Open with attribution | ✅ |
| KMA / data.go.kr | Open with attribution | ✅ |
| AirKorea / data.go.kr | Open with attribution | ✅ |
| MOLIT / data.go.kr | Open with attribution | ✅ |
| MFDS / KOGL Type 1 | Open with attribution | ✅ |
| TourAPI | Open with attribution + non-broker T&C | ✅ |
| Seoul OpenData | KOGL Type 1 | ✅ |
| Opinet | Open with daily quota | ✅ (1,500 shared/day) |
| VWorld / 국토교통부 공간정보 | Open with attribution + non-bulk T&C §10-3 | ✅ |

---

## Project status

- **Version**: 0.4.0 (15 sources / 55 tools — added VWorld 공간정보: search/geocode + 박물관·미술관 1,534건)
- **Source**: [github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea](https://github.com/jayjodev/vivory-mcp/tree/main/packages/mcp-server-korea)
- **License**: MIT (wrapper) / per-source license for upstream data
- **Roadmap**: see "Coming next" above
- **Registries**: PyPI · Official MCP Registry (`io.github.jayjodev/vivory-mcp-korea`) · awesome-mcp-servers

🇰🇷 Built in Seoul · 🌐 [vivory.app](https://vivory.app)
