# Vivory Verification MCP — Examples

Drop-in recipes that wire the 98-tool Vivory Verification gateway into
the most common agent stacks. Each file is self-contained, MIT-licensed,
and minimal enough that you can read it in one sitting.

| File                                                                                   | Audience                                          | Lines |
|----------------------------------------------------------------------------------------|---------------------------------------------------|-------|
| [`quickstart.md`](quickstart.md)                                                       | First-time MCP user — install + first call        | ~120  |
| [`claude-code-verify-before-publish.md`](claude-code-verify-before-publish.md)         | Claude Code subagent (drop into `.claude/agents/`)| ~80   |
| [`cursor-verify.mdc`](cursor-verify.mdc)                                               | Cursor rule (drop into `.cursor/rules/`)          | ~80   |
| [`langgraph-verification-node.py`](langgraph-verification-node.py)                     | LangGraph node — Python state-graph step          | ~200  |

## Picking a recipe

```
Does your agent run on Claude Code? ───── yes ──► claude-code-verify-before-publish.md
                │
                no
                ▼
Does your agent run on Cursor? ──────────── yes ──► cursor-verify.mdc
                │
                no
                ▼
Is your pipeline in LangGraph? ──────────── yes ──► langgraph-verification-node.py
                │
                no
                ▼
                              quickstart.md (framework-agnostic MCP)
```

## Required setup (shared)

```bash
pip install vivory-mcp-verification          # or: uv tool install
```

That's it. The MCP server proxies the public gateway at
`api.vivory.app/api/verify/*` — 100 anonymous calls/day per IP, no
signup required. Add an API key (`VIVORY_API_KEY` env) for 10k/day Pro
tier ($29/mo USDC, no auto-renew, no custody).

## Contributing a recipe

If you wire Vivory into a stack that's not represented here — please
PR your recipe back. The shape is: ~50–200 lines, a single example
artifact, and a short comment block at the top explaining how to use
it. License under MIT so anyone can lift the code.

## Why this exists

Most LLM citations are never checked. The Vivory bet: a uniform
verification trail is the durable moat for AI-generated content.
These recipes are the friction-zero entry point — copy, paste, ship.
