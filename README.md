# AI Agent Series

> What's actually inside an "AI agent"? No frameworks, no magic -- just a loop, a model, and one new mechanism added at a time.

Most agent frameworks hide the interesting part behind an abstraction.
This repo builds the same capabilities they offer -- memory, tools, RAG, multi-step reasoning, evals -- from scratch, one small stage at a time, so each piece is legible before it's automated away.

## Structure

Every stage lives in its own self-contained folder under `agents/`, adds exactly one new mechanism on top of the last, and ships with a blog post in `docs/` explaining *why* that mechanism works the way it does -- not just what the code does.

- **Code**: [`agents/`](agents/) -- one folder per stage.
- **Posts**: [`docs/`](docs/) -- published via GitHub Pages.
- **Roadmap**: [ROADMAP.md](ROADMAP.md) -- full stage-by-stage design rationale.

See [CLAUDE.md](CLAUDE.md) for repo conventions and commands.

## Stages

| # | Stage | Status | Code | Post |
|---|-------|--------|------|------|
| 001 | echo-loop | Built | [agents/agent-001-echo-loop](agents/agent-001-echo-loop) | [The Echo Loop](docs/_posts/2026-06-25-agent-001-echo-loop.md) |
| 002 | llm-call | Built | [agents/agent-002-llm-call](agents/agent-002-llm-call) | [The LLM Call](docs/_posts/2026-06-26-agent-002-llm-call.md) |
| 003 | conversation-history (short-term memory) | Planned | -- | -- |
| 004 | system-prompt | Planned | -- | -- |
| 005 | single-tool-call | Planned | -- | -- |
| 006 | tool-result-loop | Planned | -- | -- |
| 007 | RAG (long-term memory) | Planned | -- | -- |
| 008 | multi-tool-dispatch | Planned | -- | -- |
| 009 | malformed-tool-call-handling | Planned | -- | -- |
| 010 | persistent-session | Planned | -- | -- |
| 011 | evals-and-tracing | Planned | -- | -- |
| 012 | capstone | Planned | -- | -- |

Details on what each planned stage covers and why it's scoped the way it is live in [ROADMAP.md](ROADMAP.md).
