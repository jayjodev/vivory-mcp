# Verification MCP — PyPI publish workflow handoff

Operator action — the publish workflow lives in the **public mirror repo** `jayjodev/vivory-mcp`, not in this monorepo. The monorepo only mirrors source via `.github/workflows/sync-mcp-public.yml`.

Per the 2026-05-12 audit (`project_mcp_audit_2026_05_12.md`):
> sync-mcp-public.yml 은 source mirror 만 동기. public repo (jayjodev/vivory-mcp) 의 PyPI publish workflow 가 korea 만 처리. verification subtree 도 publish 하도록 public repo workflow 추가 필요.

## What to add in the public repo

Append a `publish-verification` job to the existing publish workflow (or add a new file at `.github/workflows/publish-verification.yml`). The reference YAML below targets a tag-triggered release of the `vivory-mcp-verification` package using PyPA Trusted Publishing — same model the public repo already uses for `vivory-mcp-korea`.

```yaml
name: Publish vivory-mcp-verification to PyPI

on:
  push:
    tags:
      - 'verification-v*'      # e.g. tag: verification-v0.4.0
  workflow_dispatch:           # operator manual trigger

permissions:
  contents: read
  id-token: write              # Trusted Publishing (no PYPI_TOKEN needed)

jobs:
  build-and-publish:
    name: Build sdist + wheel, publish to PyPI
    runs-on: ubuntu-latest
    environment: pypi          # binds to PyPI trusted-publisher project config
    defaults:
      run:
        working-directory: packages/mcp-server-verification

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install build deps
        run: pip install --upgrade build

      - name: Build sdist + wheel
        run: python -m build

      - name: Publish to PyPI (Trusted Publishing)
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: packages/mcp-server-verification/dist/
```

## One-time setup on PyPI side

1. Visit https://pypi.org/manage/project/vivory-mcp-verification/settings/publishing/
2. Add a trusted publisher:
   - **Owner**: `jayjodev`
   - **Repository name**: `vivory-mcp`
   - **Workflow filename**: `publish-verification.yml` (or the merged-job filename if you appended)
   - **Environment name**: `pypi`
3. On the GitHub side, create the `pypi` environment under `Settings → Environments` in `jayjodev/vivory-mcp` (no secrets needed — Trusted Publishing uses short-lived OIDC tokens).

## Tagging convention

Use a prefixed tag so the workflow only fires for verification releases (avoiding accidental fires when bumping `vivory-mcp-korea`):

```bash
# In the public repo
git tag verification-v0.4.0 -m "vivory-mcp-verification v0.4.0 — 45 tools / 18 categories (apt MOLIT added)"
git push origin verification-v0.4.0
```

Korea MCP already uses an analogous `korea-v*` pattern — keep that convention symmetric.

## Verification after publish

```bash
# Smoke-test that the new version is fetchable
pip index versions vivory-mcp-verification     # should list 0.4.0
uvx vivory-mcp-verification --help             # should print the server's usage
```

Update `src/frontend-api/app/mcp/page.tsx` to drop the "PyPI publish pending" note for the Verification card once 0.4.0 is live on PyPI.

## Why this lives here

This scaffold ships *in the monorepo* alongside the package so that the next operator session can find it without re-deriving the gap from memory. The actual workflow file must be added to the **public** repo (`jayjodev/vivory-mcp`) — putting it under `src/mcp-server-verification/.github/workflows/` in the monorepo would not work because GitHub Actions only reads `.github/workflows/` at repo root.

## Status

- Verification MCP source: `0.4.0` in `pyproject.toml` and `__init__.py` (monorepo + public mirror via auto-sync)
- PyPI: **not yet published**. `uvx vivory-mcp-verification` does not work yet — only direct gateway calls (`api.vivory.app/api/verify/*`) work.
- Korea MCP (sibling): published, `uvx vivory-mcp-korea` works. Follow the same pattern.
