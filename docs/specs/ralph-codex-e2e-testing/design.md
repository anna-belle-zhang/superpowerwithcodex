# Ralph-Codex-E2E Testing Design

## Architecture

Two complementary test tiers:

**Tier 1 — Skill document tests**
Subagent scenarios per writing-skills TDD methodology. A subagent receives the skill loaded and a scenario prompt; we observe whether it applies the skill correctly. Tests are documented as markdown in `tests/skills/ralph-codex-e2e-baseline.md` (RED) and `tests/skills/ralph-codex-e2e-green.md` (GREEN).

**Tier 2 — Real stack integration tests**
Toy projects in `tests/e2e/ralph-codex-e2e/`, each engineered for a specific scenario. Tests invoke the actual Ralph loop and assert on observable outputs.

## Components

### Skill Document Test Suite (`tests/skills/`)

6 scenarios covering: ralph-loop command construction, prerequisite checking, when-not-to-use routing, E2E strategy detection, retry chain escalation, and post-loop verification steps.

### Real Stack Integration Test Suite (`tests/e2e/ralph-codex-e2e/`)

4 toy projects:

| Project | Engineered condition | Stack requirement |
|---|---|---|
| `happy-path/` | No failure injection | Ralph + Codex + bash |
| `unit-retry/` | Strict `DivisionByZeroError` test Codex misses first try | Ralph + Codex + Jest |
| `e2e-retry/` | `X-Version: 1` header Codex omits without being told | Ralph + Codex + Playwright |
| `exhaustion/` | Contradictory test assertions (impossible to satisfy) | Ralph + Codex + Jest |

Each project contains: `plan.md`, pre-written test files, stub implementation, `expected-outcome.md`, `reset.sh`.

### Test Runner (`tests/e2e/ralph-codex-e2e/run-tests.sh`)

Iterates each toy project: invokes Ralph loop, captures stdout, asserts against git log and log file, reports PASS/FAIL.

## Data Flow

```
run-tests.sh
  └─ cd happy-path/
      └─ /ralph-loop "Execute plan: plan.md ..."
          ├─ Ralph → Codex (implement + unit tests)
          ├─ Ralph → Claude (E2E tests)
          └─ Ralph exits with DONE or escalation
  └─ assert: git log, log file, retry count
  └─ reset.sh (restore baseline)
```

## Error Handling

- `exhaustion/` project verifies the escalation path: Ralph exits without DONE and outputs a human escalation message
- `reset.sh` uses `git checkout` to restore stubs; must be run between test executions
- If Ralph or Codex is unavailable, test runner reports infrastructure error (not test failure)

## Dependencies

- Ralph Wiggum plugin installed (`ralph-loop@claude-plugins-official`)
- Codex MCP configured in `.mcp.json` with `codex-subagent`
- `~/.codex/config.toml` with `[sandbox_workspace_write] network_access = true`
- Jest (Node.js toy projects), Playwright (`e2e-retry` project)
