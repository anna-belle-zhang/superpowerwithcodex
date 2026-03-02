# Ralph-Codex-E2E Testing Design

**Date:** 2026-03-02
**Status:** Design Complete
**Goal:** Comprehensive test coverage for the ralph-codex-e2e skill — both the skill document and the real pipeline

---

## 1. Overall Architecture

Two complementary test tiers:

**Tier 1 — Skill document tests** (fast, no live tools needed)
Subagent scenarios per writing-skills methodology. Test that the skill correctly guides agents: right `/ralph-loop` command construction, prerequisite checking, E2E detection, when-not-to-use, retry chain escalation, post-loop verification. Documented as markdown scenarios in `tests/skills/ralph-codex-e2e-baseline.md` and `tests/skills/ralph-codex-e2e-green.md`.

**Tier 2 — Real stack integration tests** (slow, requires Ralph + Codex)
Toy projects in `tests/e2e/ralph-codex-e2e/`, each engineered for a specific scenario. Tests invoke the actual Ralph loop and assert on observable outputs: git commit history, test logs, "DONE" signal, retry counts.

The tiers are complementary — skill doc tests catch "does the skill teach the right thing?" while real stack tests catch "does the actual pipeline work?".

---

## 2. Toy Project Suite

Four toy projects in `tests/e2e/ralph-codex-e2e/`:

### Project 1: `happy-path/`

**Type:** Node.js CLI tool
**Project:** `greet.js` stub — implement `greet(name)` function
**Tests:** Jest unit tests + bash E2E (`node greet.js Alice` → assert output)
**Expected:** Codex passes everything first try
**Validates:** Golden path end-to-end

### Project 2: `unit-retry/`

**Type:** Node.js module
**Project:** `calculator.js` stub — implement `divide(a, b)`
**Engineered failure:** Pre-written tests include `divide(0, 0)` → must throw `DivisionByZeroError` (not generic `Error`). Codex frequently misses the specific error type on first attempt.
**Tests:** Jest unit tests + bash E2E sanity check
**Expected:** Unit test retry count ≥ 1, final tests green
**Validates:** Unit test retry path

### Project 3: `e2e-retry/`

**Type:** Express API with Playwright E2E
**Project:** `server.js` stub — implement `GET /status`
**Engineered failure:** E2E tests assert `X-Version: 1` response header. Codex won't include it without being told — Claude fails E2E first try, retries with header requirement, passes on attempt 2.
**Tests:** Jest unit tests + Playwright E2E
**Expected:** E2E retry count = 1, Playwright passes on attempt 2
**Validates:** E2E retry path, Playwright detection

### Project 4: `exhaustion/`

**Type:** Node.js module
**Project:** Stub with contradictory test requirements (function must return both `true` AND `false`)
**Engineered failure:** Impossible requirements exhaust all retries
**Tests:** Jest unit tests (contradictory assertions)
**Expected:** Ralph exits WITHOUT "DONE", outputs human escalation message, max iterations reached
**Validates:** Exhaustion path and human escalation

Each project contains:
- `plan.md` — the task plan for Ralph to execute
- `tests/` — pre-written test files
- `src/` — stub implementation (starting point)
- `expected-outcome.md` — assertion spec
- `reset.sh` — restores project to baseline between runs

---

## 3. Assertions

**Observable outputs:**

| Observable | How to capture |
|---|---|
| "DONE" signal | Ralph exit stdout log |
| Git commit history | `git log --oneline` after loop exits |
| Retry count | Ralph iteration counter in output |
| Test pass/fail | Saved test output logs per task |
| Human escalation | Ralph exits without "DONE", escalation message in log |

**Per-project pass criteria:**

| Project | DONE? | Commits | Retries | Final tests |
|---|---|---|---|---|
| `happy-path` | ✅ | 1 | 0 | green |
| `unit-retry` | ✅ | 1 | unit ≥ 1 | green |
| `e2e-retry` | ✅ | 1 | E2E = 1 | green |
| `exhaustion` | ❌ | 0 | max | escalation msg |

**Test runner:** `tests/e2e/ralph-codex-e2e/run-tests.sh`
1. `cd` into each toy project
2. Invoke `/ralph-loop` with project's `plan.md`
3. Capture stdout to log file
4. Assert against git log + log file
5. Report PASS/FAIL per scenario

---

## 4. Skill Document Test Scenarios

Six subagent scenarios:

### S1 — Construct the ralph-loop command
**Given:** A plan file path and specs directory
**Test:** Does agent construct correct `/ralph-loop "..."` with `--max-iterations`, `--completion-promise "DONE"`, and the per-task Codex/Claude phase structure?
**Baseline expected failure:** Vague prompt missing per-task structure

### S2 — Prerequisites checklist
**Given:** Project missing `~/.codex/config.toml` (Codex network not configured)
**Test:** Does agent catch missing prerequisite before starting?
**Baseline expected failure:** Agent proceeds without verifying prerequisites

### S3 — When NOT to use
**Given:** User says "I need human review between tasks"
**Test:** Does agent redirect to `codex-subagent-driven-development` instead of ralph-codex-e2e?
**Baseline expected failure:** Agent uses ralph-codex-e2e anyway

### S4 — E2E strategy detection
**Given:** Project with `playwright.config.ts` (then separately: project with `openapi.yaml`)
**Test:** Does agent select the correct E2E strategy for each?
**Baseline expected failure:** Agent defaults to bash regardless of project type

### S5 — Retry chain escalation
**Given:** E2E has failed twice, Claude has retried twice, still failing
**Test:** Does agent let Ralph loop (not commit with failing tests)?
**Baseline expected failure:** Agent commits with failing tests to "move on"

### S6 — Post-loop verification
**Given:** Ralph has exited with "DONE", specs directory exists
**Test:** Does agent run `superpowers:verify-specs` then `superpowers:finishing-a-development-branch`?
**Baseline expected failure:** Agent stops at "DONE" without post-loop steps

---

## 5. Files to Create

### Skill document tests
- `tests/skills/ralph-codex-e2e-baseline.md` — baseline behavior (no skill)
- `tests/skills/ralph-codex-e2e-green.md` — green phase results

### Real stack integration tests
```
tests/e2e/ralph-codex-e2e/
  run-tests.sh                    # Test runner
  happy-path/
    plan.md
    src/greet.js                  # stub
    tests/greet.test.js
    tests/e2e.sh
    expected-outcome.md
    reset.sh
  unit-retry/
    plan.md
    src/calculator.js             # stub
    tests/calculator.test.js      # strict DivisionByZeroError test
    tests/e2e.sh
    expected-outcome.md
    reset.sh
  e2e-retry/
    plan.md
    src/server.js                 # stub
    tests/server.test.js
    tests/e2e.spec.ts             # Playwright, asserts X-Version header
    playwright.config.ts
    expected-outcome.md
    reset.sh
  exhaustion/
    plan.md
    src/paradox.js                # stub
    tests/paradox.test.js         # contradictory assertions
    expected-outcome.md
    reset.sh
```

---

## 6. Success Criteria

- ✅ All 6 skill document scenarios pass with skill loaded
- ✅ `happy-path` exits with DONE, 1 commit, 0 retries
- ✅ `unit-retry` exits with DONE, unit retry count ≥ 1
- ✅ `e2e-retry` exits with DONE, E2E retry count = 1, Playwright detected correctly
- ✅ `exhaustion` exits WITHOUT DONE, human escalation message present
- ✅ `reset.sh` in each project restores clean baseline between runs
