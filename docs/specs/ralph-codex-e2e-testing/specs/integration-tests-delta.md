# Real Stack Integration Tests Delta Spec

## ADDED

### Happy Path — Pipeline Completes First Try
GIVEN the `happy-path/` toy project is at baseline (stub implementation), Ralph + Codex are available, and the plan has one task (implement `greet(name)`)
WHEN the Ralph-Codex-E2E workflow runs against the project
THEN Ralph exits with "DONE", exactly 1 commit appears in git history, unit tests pass, bash E2E passes, and retry count is 0

### Unit Retry Path — Unit Test Failure Triggers Retry
GIVEN the `unit-retry/` toy project is at baseline (stub `calculator.js`), the pre-written tests assert `divide(0, 0)` throws `DivisionByZeroError`, and the plan has one task (implement `divide(a, b)`)
WHEN the Ralph-Codex-E2E workflow runs against the project
THEN Ralph exits with "DONE", unit retry count is ≥ 1, final unit tests are green, and exactly 1 commit appears in git history

### E2E Retry Path — E2E Failure Triggers Claude Retry
GIVEN the `e2e-retry/` toy project is at baseline (stub `server.js`), Playwright E2E tests assert `X-Version: 1` response header, and the plan has one task (implement `GET /status`)
WHEN the Ralph-Codex-E2E workflow runs against the project
THEN Playwright E2E fails on attempt 1, Claude retries, Playwright E2E passes on attempt 2, Ralph exits with "DONE", and E2E retry count equals 1

### E2E Strategy Auto-Detection (Playwright)
GIVEN the `e2e-retry/` toy project contains `playwright.config.ts`
WHEN Claude selects the E2E strategy during the workflow
THEN Claude uses `npx playwright test` (not bash default)

### Exhaustion Path — All Retries Exhausted
GIVEN the `exhaustion/` toy project is at baseline (stub with contradictory test assertions), and the plan has one task with impossible requirements
WHEN the Ralph-Codex-E2E workflow runs against the project
THEN Ralph exits WITHOUT outputting "DONE", a human escalation message appears in the output, max iterations are reached, and 0 commits appear in git history

### Baseline Reset Between Runs
GIVEN any toy project has been run (commits made, files modified)
WHEN `reset.sh` is executed in that project directory
THEN the stub implementation is restored, test output files are deleted, and git history is reset to the pre-run baseline

### Test Runner Reports Per-Scenario Results
GIVEN all four toy projects are at baseline
WHEN `run-tests.sh` is executed
THEN the runner outputs a PASS or FAIL result for each of the four scenarios and exits with a non-zero code if any scenario fails
