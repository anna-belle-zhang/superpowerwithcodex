# Ralph-Codex-E2E Testing Proposal

## Intent

The ralph-codex-e2e skill exists but has no tests — neither for the skill document itself nor for the pipeline it orchestrates. This creates two risks: the skill may guide agents incorrectly (skill doc gaps), and the real Ralph+Codex+Claude pipeline may break without detection. This proposal adds comprehensive test coverage for both.

## Scope

**In scope:**
- 6 subagent skill document test scenarios (does the skill guide agents correctly?)
- 4 real-stack integration test projects (does the actual pipeline work?)
- A bash test runner with per-project assertions
- Reset scripts for repeatable runs

**Out of scope:**
- Testing Ralph loop plugin internals
- Testing Codex MCP server internals
- CI automation (tests require live Ralph + Codex stack)
- Performance or load testing

## Impact

- **Users affected:** Contributors to superpowerwithcodex who use or modify ralph-codex-e2e
- **Systems affected:** `tests/skills/`, `tests/e2e/ralph-codex-e2e/` (new directories)
- **Risk:** Low — adds test files only, no production code changes

## Success Criteria

- [ ] All 6 skill document scenarios pass with skill loaded (GREEN phase)
- [ ] `happy-path` toy project exits with DONE, 1 commit, 0 retries
- [ ] `unit-retry` toy project exits with DONE, unit retry count ≥ 1
- [ ] `e2e-retry` toy project exits with DONE, E2E retry count = 1, Playwright detected
- [ ] `exhaustion` toy project exits WITHOUT DONE, escalation message present
- [ ] `reset.sh` in each project restores clean baseline between runs
