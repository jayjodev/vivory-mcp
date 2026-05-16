# Verification MCP — PyPI publish status

The publish workflow lives in the **public mirror repo** (`jayjodev/vivory-mcp`) at
`.github/workflows/publish-mcp-verification.yml`. The monorepo only mirrors source via
`.github/workflows/sync-mcp-public.yml`. The local `.github-mirror/publish-verification.yml`
drop-in was deleted 2026-05-16 — the public repo settled on a different naming convention
(`mcp-verification-v*` + `publish-mcp-verification.yml`, not the original `verification-v*` +
`publish-verification.yml`), and a stale drop-in would mislead the next operator session.

## Status (2026-05-16)

- Monorepo source: `0.4.0` in `pyproject.toml` and `__init__.py`
- Public-repo mirror: `0.4.0` (auto-synced by `sync-mcp-public.yml`)
- Local sanity check: `python -m build` clean, `pytest tests/` 99 passed, `vivory-mcp-verification --help` smoke OK
- Public-repo workflow file: present
- Public-repo GitHub `pypi` environment: present (korea + kosis use it)
- **PyPI trusted publisher**: not yet registered (PyPI shows no `vivory-mcp-verification` project)
- Existing tag `mcp-verification-v0.2.0` on remote: leftover from a pre-config attempt — ignore, push fresh `mcp-verification-v0.4.0`

## Remaining operator action

One step. ~2 minutes in browser.

**PyPI pending publisher**: <https://pypi.org/manage/account/publishing/> → *Add a new pending publisher*

| Field | Exact value |
|---|---|
| PyPI Project Name | `vivory-mcp-verification` |
| Owner | `jayjodev` |
| Repository name | `vivory-mcp` |
| Workflow filename | `publish-mcp-verification.yml` |
| Environment name | `pypi` |

After that, the release tag can be pushed from any `jayjodev/vivory-mcp` clone:

```bash
git tag mcp-verification-v0.4.0
git push origin mcp-verification-v0.4.0
```

The workflow fires automatically, builds, and publishes via OIDC Trusted Publishing
(no `PYPI_API_TOKEN` needed).

## Verification after publish

```bash
pip index versions vivory-mcp-verification   # should list 0.4.0
uvx vivory-mcp-verification --help           # should print server usage
```

Then in this monorepo, flip the "PyPI publish 대기" note at
[src/frontend-api/app/mcp/page.tsx:46](../frontend-api/app/mcp/page.tsx#L46) to "v0.4.0 LIVE on PyPI".

## Why no token

PyPI Trusted Publishing uses GitHub OIDC short-lived tokens scoped to the `pypi` environment
in `jayjodev/vivory-mcp`. Same pattern that already published `vivory-mcp-korea` 0.3.1 and
`vivory-mcp-kosis` 0.1.0.
