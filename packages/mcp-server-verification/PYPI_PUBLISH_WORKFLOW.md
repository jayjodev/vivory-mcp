# Verification MCP — PyPI publish status

**Status 2026-05-16**: `vivory-mcp-verification` **0.4.1 LIVE on PyPI**. Install:

```bash
pip install vivory-mcp-verification
# or
uvx vivory-mcp-verification --help
```

The publish workflow lives in the **public mirror repo** (`jayjodev/vivory-mcp`) at
`.github/workflows/publish-mcp-verification.yml`. The monorepo only mirrors source via
`.github/workflows/sync-mcp-public.yml`. See [reference-api-key-store.md](../../../.claude_personal/projects/-home-ubuntu-vivory/memory/reference_api_key_store.md) for the GitHub PAT location (the same one drives `VIVORY_MCP_SYNC_TOKEN`).

## How the publish was actually run (2026-05-16)

1. Source bump to v0.4.0 + monorepo push — sync mirrored to public repo (`76bd97b`).
2. Tag `mcp-verification-v0.4.0` push to mirror → publish workflow fired → **PyPI rejected with `400 'summary' field must be 512 characters or less`**. The pyproject `description` was 570 chars (the exhaustive tool list); PyPI's `summary` field has a 512-char hard limit. The wheel itself built fine; metadata validation killed the upload.
3. Description trimmed to 444 chars (no tool surface change, mission framing intact) + version bumped 0.4.0 → 0.4.1. Old 0.4.0 stays a dead release name; tag stays on the mirror as historical context.
4. Tag `mcp-verification-v0.4.1` push → publish workflow #2 → green → PyPI 0.4.1 live.

## Trusted Publisher config (one-time, already done)

PyPI <https://pypi.org/manage/account/publishing/> shows:
- PyPI Project: `vivory-mcp-verification`
- Owner: `jayjodev`
- Repository name: `vivory-mcp`
- Workflow filename: `publish-mcp-verification.yml`
- Environment name: `pypi`

GitHub `jayjodev/vivory-mcp` Settings → Environments → `pypi` (no secrets, OIDC only). Same pattern used by `vivory-mcp-korea` and `vivory-mcp-kosis`.

## Release flow for the next version

```bash
# 1. Bump version in src/mcp-server-verification/pyproject.toml + __init__.py
# 2. Keep description ≤ 512 chars
# 3. Local sanity:
cd src/mcp-server-verification
python3 -m build
python3 -m venv /tmp/v && /tmp/v/bin/pip install -e ".[dev]" && /tmp/v/bin/pytest -q tests/
/tmp/v/bin/vivory-mcp-verification --help
# 4. Commit + push monorepo (sync workflow mirrors to public repo)
git add src/mcp-server-verification/{pyproject.toml,src/vivory_mcp_verification/__init__.py}
git commit -m "feat(mcp-verification): vX.Y.Z — ..."
git push origin main
# 5. After sync workflow completes, tag and push on the mirror clone:
cd /tmp/vivory-mcp && git pull --rebase
git tag mcp-verification-v<X.Y.Z>
git push origin mcp-verification-v<X.Y.Z>
# 6. Watch publish workflow on jayjodev/vivory-mcp Actions tab
# 7. pip index versions vivory-mcp-verification    # should list new version
```

## Gotchas

- **PyPI summary 512-char limit** — pyproject `description` field. Long tool lists belong in README (`long_description`), not summary.
- **`mcp-verification-v0.2.0` stale tag** on the mirror — pre-config attempt, never published. Ignore.
- **Tag prefix is `mcp-verification-v*`** (not `verification-v*`). Must match the workflow's `on.push.tags` glob.
- **Rerun-failed-jobs uses the original commit** — if you need to retry with a fresh fix, bump version + new tag rather than relying on rerun.
