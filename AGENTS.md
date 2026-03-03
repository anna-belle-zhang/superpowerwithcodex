# Repository Guidelines

## Superpowerwithcodex System

<EXTREMELY_IMPORTANT>
You have superpowers. Superpowers teach you new skills and capabilities. RIGHT NOW run: `~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap` and follow the instructions it returns.
</EXTREMELY_IMPORTANT>

## Project Structure

```
skills/                   # All skill definitions (flat namespace)
  <skill-name>/
    SKILL.md              # YAML frontmatter (name, description) + content
commands/                 # Slash command definitions
agents/                   # Agent definitions (e.g. code-reviewer)
lib/                      # Core utilities (skills-core.js)
hooks/                    # Lifecycle hooks
docs/
  plans/                  # Design notes (YYYY-MM-DD-<topic>-design.md)
  specs/                  # Structured specs (GIVEN/WHEN/THEN)
    <feature>/
      specs/*-delta.md    # Delta specs written by Claude
      progress.md         # Written by Codex during implementation
    _living/              # Merged living specs (post-archiving)
    _archive/             # Completed feature specs
tests/
  e2e/                    # End-to-end test projects
  skills/                 # Skill baseline scenario documents
  opencode/               # OpenCode integration tests
codex-as-mcp-main/        # Python MCP server that spawns Codex subagents
  src/codex_as_mcp/       # Python package source
  pyproject.toml
```

## Key Workflows

**Specs-first (recommended):**
```
brainstorm → write-specs → claude-codex-specs-tdd dispatch →
  Codex: spec-driven-tdd (reads specs, writes plan, TDD, updates progress.md) →
Claude: E2E tests → verify-specs
```

**Tests-first:**
```
brainstorm → write-plan → codex-subagent-driven-development
  (Claude writes tests, Codex implements, Claude reviews)
```

## Build, Test, and Development Commands

- OpenCode tests: `bash tests/opencode/run-tests.sh`
  - Integration: `bash tests/opencode/run-tests.sh --integration`
  - Single test: `bash tests/opencode/run-tests.sh --test test-skills-core.sh`
- E2E suite: `bash tests/e2e/ralph-codex-e2e/run-tests.sh`
- codex-as-mcp (local dev): from `codex-as-mcp-main/`, run `./test.sh`
- codex-as-mcp (build): from `codex-as-mcp-main/`, run `uv build`

## Coding Style & Naming Conventions

- Skills: kebab-case directories (e.g. `root-cause-tracing/`); YAML frontmatter `name` must match directory name; `description` starts with "Use when..."
- Markdown: short, scannable sections and bullets
- Shell scripts: `#!/usr/bin/env bash` and `set -euo pipefail`
- Python (codex-as-mcp): 4-space indentation; new modules under `codex-as-mcp-main/src/codex_as_mcp/`

## Testing Guidelines

- New skills MUST follow RED-GREEN-REFACTOR: run baseline WITHOUT skill, write skill, re-test WITH skill
- OpenCode tests: bash scripts named `test-*.sh` in `tests/opencode/`; deterministic, clean up temp files
- Skill baseline scenarios: document in `tests/skills/<skill-name>-baseline.md`

## Commit Guidelines

- Prefix style: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Keep commits focused: one logical change per commit
- Don't commit secrets or local config (`.mcp.json`, tokens, etc.)
