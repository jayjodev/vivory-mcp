# vivory-mcp-verification (discontinued)

<!-- mcp-name: io.github.jayjodev/vivory-mcp-verification -->

**This package no longer works.** The hosted API it called (`api.vivory.app`)
was shut down on **2026-08-09**. Every tool in versions up to 0.14.0 now fails,
because that address only redirects to the vivory.app home page.

There is no paid plan. "Tools Pro" is not sold anymore, and no new keys are
issued.

## What 0.15.0 does

This final release exists so that nobody is left with a server that fails
quietly. It starts, prints this notice to stderr, and exposes a single tool,
`service_status`, that returns the same notice to your agent. It makes no
network calls.

## What you should do

Remove `vivory-mcp-verification` from your MCP client configuration
(Claude Desktop, Claude Code, Cursor, and so on). Older versions stay on PyPI
so that pinned installs do not break, but none of them can reach a server.

The sibling packages `vivory-mcp-korea` and `vivory-mcp-kosis` were
discontinued earlier.

## 한국어

이 패키지는 더 이상 동작하지 않습니다. 호출하던 API(`api.vivory.app`)가
2026-08-09 에 종료되었습니다. 유료 플랜(Tools Pro)도 더 이상 판매하지 않습니다.
MCP 클라이언트 설정에서 이 서버를 지워 주세요.

문의: contact@vivory.app · 비보리랩 (Vivory Lab)

## License

MIT
