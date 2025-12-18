# Repository Guidelines

## Project Structure & Module Organization

This repository is a small “meta workspace” containing two primary projects:

- `superpowers-main/`: the Superpowers skills + plugin content
  - `skills/<skill-name>/SKILL.md`: individual skills (directory name is kebab-case; frontmatter `name:` should match)
  - `lib/`, `commands/`, `agents/`, `hooks/`: supporting runtime content and templates
  - `tests/opencode/`: shell-based test suite for the OpenCode plugin integration
- `codex-as-mcp-main/`: a Python MCP server that spawns Codex subagents
  - `src/codex_as_mcp/`: Python package source (src layout)
  - `pyproject.toml`: packaging metadata
  - `test.sh`: helper for running MCP Inspector against the local server
- `docs/plans/`: design notes and project planning documents

## Build, Test, and Development Commands

- Superpowers (OpenCode tests): `bash superpowers-main/tests/opencode/run-tests.sh`
  - Run integration tests: `bash superpowers-main/tests/opencode/run-tests.sh --integration`
  - Run one test: `bash superpowers-main/tests/opencode/run-tests.sh --test test-skills-core.sh`
- codex-as-mcp (local dev): from `codex-as-mcp-main/`, run `./test.sh` (starts MCP Inspector + local server via `uv`)
- codex-as-mcp (build package): from `codex-as-mcp-main/`, run `uv build`

## Coding Style & Naming Conventions

- Markdown: keep headings descriptive; prefer short, scannable sections and bullets.
- Skills: use kebab-case directories (e.g. `root-cause-tracing/`) and keep the YAML frontmatter accurate (`name`, `description`).
- Shell scripts: use `#!/usr/bin/env bash` and `set -euo pipefail`; keep scripts runnable via `bash path/to/script.sh`.
- Python (codex-as-mcp): 4-space indentation; keep new modules under `codex-as-mcp-main/src/codex_as_mcp/`.

## Testing Guidelines

- OpenCode tests are bash scripts named `test-*.sh` in `superpowers-main/tests/opencode/`; ensure new tests are deterministic and clean up temp files.
- For codex-as-mcp, prefer exercising behavior via `codex-as-mcp-main/test.sh` and MCP Inspector when changing server behavior.

## Commit & Pull Request Guidelines

- Commit messages: this repo currently uses a prefix style (example: `Design: ...`). Prefer `<Area>: <imperative summary>` (e.g. `Docs: Update install steps`).
- PRs: clearly state which subproject you changed (`superpowers-main/` vs `codex-as-mcp-main/`), include the exact commands run (and their output if relevant), and update the nearest README/SKILL docs when behavior changes.

## Security & Configuration Tips

- Don’t commit secrets or local config (tokens, `.mcp.json`, etc.). Use environment variables for credentials (for example, PyPI publishing in `codex-as-mcp-main/` expects `PYPI_USERNAME`/`PYPI_TOKEN`).
