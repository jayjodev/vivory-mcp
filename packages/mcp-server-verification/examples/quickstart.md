# Quickstart — verify your first DOI in 60 seconds

This recipe is framework-agnostic. It works with any MCP client (Claude
Code, Claude Desktop, Cursor, Continue, Cody, custom Python).

## 1. Install

```bash
pip install vivory-mcp-verification
# or:  uv tool install vivory-mcp-verification
```

The package installs a `vivory-mcp-verification` console script.

## 2. Smoke test (no MCP client, no signup)

The MCP server proxies `api.vivory.app/api/verify/*`. You can hit the
gateway directly to confirm everything works:

```bash
curl -s 'https://api.vivory.app/api/verify/doi?doi=10.1038/s41586-021-03819-2' | jq
```

Expected shape:

```json
{
  "implementation_phase": "v0.1-real",
  "checked_at": "2026-05-22T...",
  "sources": ["crossref", "openalex"],
  "data": {
    "doi": "10.1038/s41586-021-03819-2",
    "title": "Highly accurate protein structure prediction with AlphaFold",
    "year": 2021,
    "publisher": "Springer Science and Business Media LLC",
    "retracted": false
  }
}
```

If `data.retracted` is `true`, the citation is poisoned — block your
agent from quoting it.

## 3. Register the MCP with your agent

### Claude Code / Claude Desktop

Add to `~/.claude/mcp.json` (Claude Code) or the equivalent Claude
Desktop config:

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification"
    }
  }
}
```

Or one-liner via CLI:

```bash
claude mcp add vivory-verification vivory-mcp-verification
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification"
    }
  }
}
```

### Continue / Cody / other MCP-compatible

Use the same JSON shape. The command is just `vivory-mcp-verification`.

## 4. First call from inside the agent

Ask the agent (in any model that supports tool use):

> "Use vivory-verification to check whether DOI 10.1038/s41586-021-03819-2
> has been retracted, and tell me which sources confirmed that."

The agent should call `verify_doi` and `doi_retraction_check`, then
report a structured answer with the source list.

## 5. Common next tools

| Need                              | Tool                                         |
|-----------------------------------|----------------------------------------------|
| Is this DOI real / what is it?    | `verify_doi`                                 |
| Was this paper retracted?         | `doi_retraction_check`                       |
| Is this Korean company alive?     | `kor_company_status`                         |
| Was the law cited still valid?    | `kor_law_currency` / `kor_law_lookup`        |
| Korean case / bill status?        | `kor_case_search` / `kor_bill_status`        |
| Same entity across registries?    | `company_reconcile` / `person_reconcile`     |
| Recall confirmed across sources?  | `recall_reconcile`                           |
| Is this image C2PA-signed?        | `verify_c2pa`                                |
| Fingerprint a file into a receipt?| `compute_file_hash` (SHA-256/512 + IPFS CID) |
| Is this receipt chain intact?     | `verify_hash_chain`                          |

13 moat tools total — see [README.md](../README.md) for the full category
table.

## 6. Rate limits

- **Anonymous** (no key): 100 calls/day per IP. Polite for development.
- **Free** (signup at [api.vivory.app/dashboard](https://api.vivory.app/dashboard)): 500/day.
- **Tools Pro** ($4.99/mo, USDC or card, no auto-renew, no custody): 10,000/day across all 13 verification tools — single paid tier after bundle absorb 2026-06-01; the prior standalone $29/mo Vivory API Pro tier is retired.

Set the key as an env var; the MCP picks it up automatically:

```json
{
  "mcpServers": {
    "vivory-verification": {
      "command": "vivory-mcp-verification",
      "env": { "VIVORY_API_KEY": "vk_live_..." }
    }
  }
}
```

## 7. License

MIT. Lift the recipe into your codebase, fork the tools, ship.
