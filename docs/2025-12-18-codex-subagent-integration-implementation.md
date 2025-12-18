# Codex Subagent Integration - Implementation Notes (2025-12-18)

This document summarizes what was implemented from `docs/plans/2025-12-18-codex-subagent-integration.md`, what changed in the repo, and what remains as next steps.

## What Changed

### 1. Codex wrapper library (Node)

Added a new wrapper module intended to centralize “Codex via MCP” logic:

- Added: `superpowers-main/lib/codex-integration.js`

Current capabilities:
- `checkCodexAvailability()` checks:
  - `.mcp.json` exists in the current working directory
  - `mcpServers.codex-subagent` is present
  - `codex` CLI exists on PATH
- `executeWithCodex()` provides retry loop + progress callback plumbing
- `retryWithFeedback()` builds retry prompts (attempt 2 includes “research required” guidance)
- Boundary helpers:
  - `buildFileBoundaries()`
  - `formatBoundaryInstructions()`
  - `detectBoundaryViolations()`

Current limitation:
- The actual MCP call is not wired up from Node yet (`spawnCodexAgent()` is still a stub).

### 2. New workflow skill

Added a new skill describing the intended Claude-tests/Codex-implements/review workflow:

- Added: `superpowers-main/skills/codex-subagent-driven-development/SKILL.md`

Focus:
- Sequential TDD loop (RED → Codex GREEN → verify → review)
- Retry chain (Codex retries then Claude retries then escalation)
- File boundary enforcement expectations (verify diffs; revert violations)

### 3. Writing-plans execution handoff updated

Updated the plan handoff copy to prefer Codex subagents when available:

- Updated: `superpowers-main/skills/writing-plans/SKILL.md`

Changes:
- Adds “A) Codex subagents (default)” option
- Adds fallback behavior when Codex is not available
- Adds optional plan YAML frontmatter fields:
  - `execution-strategy`
  - `created`
  - `codex-available`

### 4. Tests (repo uses bash harness, not Jest)

The original plan proposed Jest tests. This repo’s established pattern is bash scripts under `superpowers-main/tests/opencode/` that run small Node snippets, so the implementation follows that.

Added:
- `superpowers-main/tests/opencode/test-codex-integration.sh` (library behavior tests)
- `superpowers-main/tests/opencode/test-codex-mcp.sh` (smoke check; optional integration)

Updated:
- `superpowers-main/tests/opencode/run-tests.sh` (includes the new library test by default; adds MCP smoke test under `--integration`)

### 5. Documentation

Added docs describing setup and usage:
- Added: `superpowers-main/docs/codex-integration.md`
- Added: `docs/codex-integration.md` (pointer doc for this meta-workspace)

Updated overview mention in:
- Updated: `superpowers-main/README.md`

Added a tiny end-to-end validation plan:
- Added: `docs/plans/2025-12-18-test-codex-integration.md`

## How To Verify

Run the non-integration test suite:

```bash
bash superpowers-main/tests/opencode/run-tests.sh
```

Run just the Codex library tests:

```bash
bash superpowers-main/tests/opencode/run-tests.sh --test test-codex-integration.sh
```

Optional integration run (requires OpenCode and includes the MCP smoke test):

```bash
bash superpowers-main/tests/opencode/run-tests.sh --integration
```

## What’s Next

### 1. Implement real MCP invocation from Node

`superpowers-main/lib/codex-integration.js` currently validates configuration and provides retry/boundary helpers, but it does not yet call the MCP tool. To finish the intended “Codex subagent integration” end-to-end:

- Choose a Node MCP client approach:
  - Add a lightweight JS MCP client dependency (preferred if this repo already has a dependency mechanism), or
  - Invoke the MCP server process directly and speak MCP over stdio (more work), or
  - Use an existing MCP client already present in the host agent runtime (if available).
- Implement `spawnCodexAgent(prompt, workingDir)` to call:
  - MCP server: `codex-subagent`
  - Tool: `spawn_agent`

### 2. Upgrade smoke test → true integration test

Once Node can call MCP:
- Replace/extend `superpowers-main/tests/opencode/test-codex-mcp.sh` to:
  - start with a temp working directory
  - call the MCP tool through the Node wrapper
  - assert that Codex actually created/modified expected files
  - always clean up temp files

### 3. Tighten boundary enforcement

Currently:
- boundary checking is implemented as a helper (`detectBoundaryViolations`)
- enforcement is documented in the skill, not automated

Next:
- Add a helper to capture changed files via git:
  - `git diff --name-only` (or `git status --porcelain`)
- Automatically revert violations and retry with stricter boundary instructions.

### 4. Make `checkCodexAvailability()` more actionable

Potential improvements:
- Check that the configured MCP command exists (`uvx`, `uv`) and report clearer errors
- Detect whether Codex is authenticated (if there’s a reliable, non-interactive check)

## Known Gaps / Constraints

- The Node wrapper does not yet perform a real MCP call; the Python server (`codex-as-mcp-main/src/codex_as_mcp/server.py`) is the current working implementation that spawns Codex.
- Network access is restricted in this environment, so “@latest” installs and online research flows may require explicit approval or a local-path config.

