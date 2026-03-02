---
execution-strategy: ralph-codex-e2e
created: 2026-03-02
specs-dir: docs/specs/ralph-codex-e2e-testing/
---

# Ralph-Codex-E2E Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the full test infrastructure for ralph-codex-e2e — four toy integration projects and the skill document test scenarios.

**Architecture:** Two-tier. Tier 1 = skill document scenarios (S1–S6, markdown files in `tests/skills/`). Tier 2 = real-stack toy projects (4 directories in `tests/e2e/ralph-codex-e2e/`), each engineered to trigger a specific pipeline behavior when ralph-codex-e2e is invoked against them.

**Tech Stack:** Node.js, Jest, Express, Playwright (@playwright/test), bash

**Specs:** `docs/specs/ralph-codex-e2e-testing/`

---

## Task 1: Create happy-path toy project

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| T1 | GIVEN `happy-path/` at baseline WHEN ralph-codex-e2e runs THEN DONE + 1 commit + 0 retries | integration-tests-delta.md |
| T6 | GIVEN project has been run WHEN reset.sh executes THEN stub restored + log deleted | integration-tests-delta.md |

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/happy-path/package.json`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/src/greet.js` (stub)
- Create: `tests/e2e/ralph-codex-e2e/happy-path/src/greet.js.stub` (backup copy)
- Create: `tests/e2e/ralph-codex-e2e/happy-path/tests/greet.test.js`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/tests/e2e.sh`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/plan.md`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/expected-outcome.md`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/reset.sh`

**Step 1: Write the failing test**

Create `tests/e2e/ralph-codex-e2e/happy-path/tests/greet.test.js`:

```javascript
const { greet } = require('../src/greet');

test('greets with name', () => {
  expect(greet('Alice')).toBe('Hello, Alice!');
});

test('greets with different name', () => {
  expect(greet('Bob')).toBe('Hello, Bob!');
});
```

**Step 2: Create supporting files**

`tests/e2e/ralph-codex-e2e/happy-path/package.json`:
```json
{
  "name": "happy-path-test",
  "version": "1.0.0",
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

`tests/e2e/ralph-codex-e2e/happy-path/src/greet.js` (stub — intentionally broken):
```javascript
function greet(name) {
  throw new Error('Not implemented');
}
module.exports = { greet };
```

`tests/e2e/ralph-codex-e2e/happy-path/src/greet.js.stub` — identical copy of the stub above (used by reset.sh).

`tests/e2e/ralph-codex-e2e/happy-path/tests/e2e.sh`:
```bash
#!/bin/bash
set -e
node -e "
const { greet } = require('./src/greet');
const result = greet('Alice');
if (result !== 'Hello, Alice!') {
  console.error('E2E FAIL: got', result);
  process.exit(1);
}
console.log('E2E PASS:', result);
"
```

`tests/e2e/ralph-codex-e2e/happy-path/plan.md`:
```markdown
# Happy Path Task Plan

## Task 1: Implement greet function

Implement `greet(name)` in `src/greet.js` to return the string `Hello, ${name}!`.

Unit tests: `npm test`
E2E: `bash tests/e2e.sh`
```

`tests/e2e/ralph-codex-e2e/happy-path/expected-outcome.md`:
```markdown
# Happy Path Expected Outcome

- Ralph exits with: DONE
- Git commits after run: 1
- Unit test retries: 0
- E2E retries: 0
- All tests final state: green
```

`tests/e2e/ralph-codex-e2e/happy-path/reset.sh`:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/greet.js.stub" "$SCRIPT_DIR/src/greet.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: happy-path stub restored"
```

**Step 3: Install dependencies and run test to verify it FAILS**

```bash
cd tests/e2e/ralph-codex-e2e/happy-path
npm install
npm test
```

Expected: FAIL — `Error: Not implemented`. This confirms the test correctly catches the unimplemented stub.

**Step 4: Verify reset.sh**

```bash
echo "modified" >> src/greet.js
bash reset.sh
grep "Not implemented" src/greet.js
```

Expected: grep finds "Not implemented" — stub is restored.

**Step 5: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/happy-path/
git commit -m "test: add happy-path toy project for ralph-codex-e2e"
```

---

## Task 2: Create unit-retry toy project

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| T2 | GIVEN `unit-retry/` at baseline WHEN ralph-codex-e2e runs THEN DONE + unit retry ≥ 1 | integration-tests-delta.md |
| T6 | GIVEN project has been run WHEN reset.sh executes THEN stub restored | integration-tests-delta.md |

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/package.json`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/src/calculator.js` (stub)
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/src/calculator.js.stub`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/tests/calculator.test.js`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/tests/e2e.sh`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/plan.md`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/expected-outcome.md`
- Create: `tests/e2e/ralph-codex-e2e/unit-retry/reset.sh`

**Step 1: Write the failing test**

Create `tests/e2e/ralph-codex-e2e/unit-retry/tests/calculator.test.js`:

```javascript
const { divide } = require('../src/calculator');

test('divides two numbers', () => {
  expect(divide(10, 2)).toBe(5);
});

test('returns float', () => {
  expect(divide(7, 2)).toBe(3.5);
});

test('throws DivisionByZeroError for 1/0', () => {
  expect(() => divide(1, 0)).toThrow('DivisionByZeroError');
});

test('throws DivisionByZeroError for 0/0', () => {
  expect(() => divide(0, 0)).toThrow('DivisionByZeroError');
});
```

Note: `toThrow('DivisionByZeroError')` matches the *message* string, not error type. Codex's first attempt typically throws `new Error('Division by zero')` or similar — close but wrong message. This reliably forces a retry.

**Step 2: Create supporting files**

`tests/e2e/ralph-codex-e2e/unit-retry/package.json`:
```json
{
  "name": "unit-retry-test",
  "version": "1.0.0",
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

`tests/e2e/ralph-codex-e2e/unit-retry/src/calculator.js` (stub):
```javascript
function divide(a, b) {
  throw new Error('Not implemented');
}
module.exports = { divide };
```

`tests/e2e/ralph-codex-e2e/unit-retry/src/calculator.js.stub` — identical copy of stub.

`tests/e2e/ralph-codex-e2e/unit-retry/tests/e2e.sh`:
```bash
#!/bin/bash
set -e
node -e "
const { divide } = require('./src/calculator');
const result = divide(10, 2);
if (result !== 5) { console.error('E2E FAIL'); process.exit(1); }
console.log('E2E PASS: 10/2 =', result);
"
```

`tests/e2e/ralph-codex-e2e/unit-retry/plan.md`:
```markdown
# Unit Retry Task Plan

## Task 1: Implement divide function

Implement `divide(a, b)` in `src/calculator.js`.

Requirements:
- Returns `a / b` for normal inputs
- When `b === 0`, throws an error with the message `DivisionByZeroError`

Unit tests: `npm test`
E2E: `bash tests/e2e.sh`
```

`tests/e2e/ralph-codex-e2e/unit-retry/expected-outcome.md`:
```markdown
# Unit Retry Expected Outcome

- Ralph exits with: DONE
- Git commits after run: 1
- Unit test retries: ≥ 1 (DivisionByZeroError message mismatch on first attempt)
- E2E retries: 0
- All tests final state: green
```

`tests/e2e/ralph-codex-e2e/unit-retry/reset.sh`:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/calculator.js.stub" "$SCRIPT_DIR/src/calculator.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: unit-retry stub restored"
```

**Step 3: Install and verify tests FAIL**

```bash
cd tests/e2e/ralph-codex-e2e/unit-retry
npm install
npm test
```

Expected: FAIL — `Error: Not implemented`. All 4 tests fail.

**Step 4: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/unit-retry/
git commit -m "test: add unit-retry toy project for ralph-codex-e2e"
```

---

## Task 3: Create e2e-retry toy project

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| T3 | GIVEN `e2e-retry/` at baseline WHEN ralph-codex-e2e runs THEN E2E fails attempt 1, passes attempt 2, DONE | integration-tests-delta.md |
| T4 | GIVEN `playwright.config.ts` exists WHEN E2E strategy selected THEN Playwright used | integration-tests-delta.md |
| T6 | GIVEN project has been run WHEN reset.sh executes THEN stub restored | integration-tests-delta.md |

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/package.json`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/playwright.config.ts`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/src/server.js` (stub)
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/src/server.js.stub`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/tests/server.test.js`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/tests/e2e.spec.ts`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/plan.md`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/expected-outcome.md`
- Create: `tests/e2e/ralph-codex-e2e/e2e-retry/reset.sh`

**Step 1: Write the failing unit test**

`tests/e2e/ralph-codex-e2e/e2e-retry/tests/server.test.js`:
```javascript
const request = require('supertest');
const app = require('../src/server');

test('GET /status returns 200', async () => {
  const res = await request(app).get('/status');
  expect(res.status).toBe(200);
  expect(res.body).toHaveProperty('status');
});
```

**Step 2: Write the Playwright E2E test**

`tests/e2e/ralph-codex-e2e/e2e-retry/tests/e2e.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';

test('GET /status returns X-Version: 1 header', async ({ request }) => {
  const response = await request.get('/status');
  expect(response.ok()).toBeTruthy();
  const headers = response.headers();
  expect(headers['x-version']).toBe('1');
});
```

Note: Codex will implement `GET /status` correctly for unit tests (status 200, body with `status`) but will not include the `X-Version: 1` header. The Playwright E2E test catches this and forces a retry. Claude's retry prompt must specify the missing header.

**Step 3: Create supporting files**

`tests/e2e/ralph-codex-e2e/e2e-retry/playwright.config.ts`:
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'node src/server.js',
    port: 3000,
    reuseExistingServer: false,
  },
});
```

`tests/e2e/ralph-codex-e2e/e2e-retry/src/server.js` (stub):
```javascript
const express = require('express');
const app = express();

app.get('/status', (req, res) => {
  // TODO: implement — must include X-Version: 1 response header
  res.status(501).json({ error: 'Not implemented' });
});

if (require.main === module) {
  app.listen(3000, () => console.log('Server running on port 3000'));
}

module.exports = app;
```

`tests/e2e/ralph-codex-e2e/e2e-retry/src/server.js.stub` — identical copy of stub.

`tests/e2e/ralph-codex-e2e/e2e-retry/package.json`:
```json
{
  "name": "e2e-retry-test",
  "version": "1.0.0",
  "scripts": {
    "test": "jest",
    "test:e2e": "npx playwright test"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "supertest": "^6.3.0",
    "@playwright/test": "^1.40.0"
  }
}
```

`tests/e2e/ralph-codex-e2e/e2e-retry/plan.md`:
```markdown
# E2E Retry Task Plan

## Task 1: Implement GET /status endpoint

Implement `GET /status` in `src/server.js` to return:
- HTTP 200
- JSON body: `{ "status": "ok" }`

Unit tests: `npm test`
E2E: `npx playwright test`
```

Note: The plan intentionally omits the `X-Version: 1` header requirement. Codex passes unit tests but Playwright E2E catches the missing header. Claude's retry feedback must mention the header.

`tests/e2e/ralph-codex-e2e/e2e-retry/expected-outcome.md`:
```markdown
# E2E Retry Expected Outcome

- Ralph exits with: DONE
- Git commits after run: 1
- Unit test retries: 0
- E2E retries: 1 (X-Version header missing on first attempt)
- E2E strategy: Playwright (detected from playwright.config.ts)
- All tests final state: green
```

`tests/e2e/ralph-codex-e2e/e2e-retry/reset.sh`:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/server.js.stub" "$SCRIPT_DIR/src/server.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: e2e-retry stub restored"
```

**Step 4: Install and verify unit test FAILS**

```bash
cd tests/e2e/ralph-codex-e2e/e2e-retry
npm install
npx playwright install --with-deps chromium
npm test
```

Expected: FAIL — `501` status, unit test fails. This confirms test catches the stub.

**Step 5: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/e2e-retry/
git commit -m "test: add e2e-retry toy project for ralph-codex-e2e"
```

---

## Task 4: Create exhaustion toy project

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| T5 | GIVEN `exhaustion/` at baseline WHEN ralph-codex-e2e runs THEN no DONE + escalation + 0 commits | integration-tests-delta.md |
| T6 | GIVEN project has been run WHEN reset.sh executes THEN stub restored | integration-tests-delta.md |

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/package.json`
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/src/paradox.js` (stub)
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/src/paradox.js.stub`
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/tests/paradox.test.js`
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/plan.md`
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/expected-outcome.md`
- Create: `tests/e2e/ralph-codex-e2e/exhaustion/reset.sh`

**Step 1: Write the contradictory tests**

`tests/e2e/ralph-codex-e2e/exhaustion/tests/paradox.test.js`:
```javascript
const { evaluate } = require('../src/paradox');

test('must return true', () => {
  expect(evaluate()).toBe(true);
});

test('must return false', () => {
  expect(evaluate()).toBe(false);
});
```

These two tests are mutually exclusive — no implementation can satisfy both. This exhausts all retries.

**Step 2: Create supporting files**

`tests/e2e/ralph-codex-e2e/exhaustion/package.json`:
```json
{
  "name": "exhaustion-test",
  "version": "1.0.0",
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

`tests/e2e/ralph-codex-e2e/exhaustion/src/paradox.js` (stub):
```javascript
function evaluate() {
  throw new Error('Not implemented');
}
module.exports = { evaluate };
```

`tests/e2e/ralph-codex-e2e/exhaustion/src/paradox.js.stub` — identical copy of stub.

`tests/e2e/ralph-codex-e2e/exhaustion/plan.md`:
```markdown
# Exhaustion Task Plan

## Task 1: Implement evaluate function

Implement `evaluate()` in `src/paradox.js`.

The function must satisfy all unit tests.

Unit tests: `npm test`
```

`tests/e2e/ralph-codex-e2e/exhaustion/expected-outcome.md`:
```markdown
# Exhaustion Expected Outcome

- Ralph exits with: NO DONE (escalation message instead)
- Git commits after run: 0
- Retries: max iterations reached
- Output must contain: human escalation message
```

`tests/e2e/ralph-codex-e2e/exhaustion/reset.sh`:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/paradox.js.stub" "$SCRIPT_DIR/src/paradox.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: exhaustion stub restored"
```

**Step 3: Install and verify tests FAIL**

```bash
cd tests/e2e/ralph-codex-e2e/exhaustion
npm install
npm test
```

Expected: FAIL — both tests fail (Not implemented). Good.

**Step 4: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/exhaustion/
git commit -m "test: add exhaustion toy project for ralph-codex-e2e"
```

---

## Task 5: Create test runner

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| T7 | GIVEN all toy projects at baseline WHEN run-tests.sh executes THEN PASS/FAIL per scenario + non-zero exit on failure | integration-tests-delta.md |

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/run-tests.sh`

**Step 1: Write the test runner**

`tests/e2e/ralph-codex-e2e/run-tests.sh`:
```bash
#!/bin/bash
# Ralph-Codex-E2E integration test runner
# Usage: bash run-tests.sh
# Requires: Ralph Wiggum plugin, Codex MCP configured, ~/.codex/config.toml with network_access=true

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0
RESULTS=()

check_prerequisites() {
  echo "Checking prerequisites..."
  if ! command -v codex &>/dev/null; then
    echo "ERROR: codex CLI not found. Install via: pip install codex-cli"
    exit 1
  fi
  if [ ! -f "$HOME/.codex/config.toml" ]; then
    echo "WARNING: ~/.codex/config.toml not found. Integration tests may fail."
  fi
  echo "Prerequisites OK"
}

run_scenario() {
  local name=$1
  local dir="$SCRIPT_DIR/$name"
  local expected="$dir/expected-outcome.md"
  local log="$dir/run.log"

  echo ""
  echo "========================================"
  echo "Scenario: $name"
  echo "========================================"

  # Reset to baseline
  bash "$dir/reset.sh"

  # Record baseline git state
  local baseline_hash
  baseline_hash=$(git -C "$SCRIPT_DIR" rev-parse HEAD)

  # Run ralph-codex-e2e against this toy project
  # NOTE: This must be invoked manually in a Claude Code session:
  #   /ralph-loop "Execute plan: tests/e2e/ralph-codex-e2e/$name/plan.md ..." --max-iterations 10
  # This runner verifies pre/post conditions only.

  echo "Pre-condition check: verifying stub fails tests..."
  local test_result=0
  (cd "$dir" && npm test 2>&1 || true) | grep -q "FAIL\|not implemented\|Not implemented\|Error" && test_result=1 || test_result=0

  if [ "$test_result" -eq 1 ]; then
    echo "  PRE-CONDITION PASS: stub correctly fails tests"
  else
    echo "  PRE-CONDITION FAIL: stub should fail tests but doesn't"
    RESULTS+=("FAIL (pre-condition): $name")
    ((FAIL++))
    return
  fi

  # Verify reset.sh works
  echo "Verifying reset.sh..."
  if bash "$dir/reset.sh" 2>&1 | grep -q "Reset complete"; then
    echo "  RESET PASS: reset.sh outputs expected message"
  else
    echo "  RESET FAIL: reset.sh did not output 'Reset complete'"
    RESULTS+=("FAIL (reset): $name")
    ((FAIL++))
    return
  fi

  echo ""
  echo "  Infrastructure verified for: $name"
  echo "  To run full scenario: invoke ralph-codex-e2e against $dir/plan.md"
  echo "  Expected outcomes documented in: $expected"

  RESULTS+=("PASS (pre-conditions): $name")
  ((PASS++))
}

check_prerequisites

run_scenario "happy-path"
run_scenario "unit-retry"
run_scenario "e2e-retry"
run_scenario "exhaustion"

echo ""
echo "========================================"
echo "RESULTS"
echo "========================================"
for r in "${RESULTS[@]}"; do
  echo "  $r"
done
echo ""
echo "Passed: $PASS / $((PASS + FAIL))"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
```

**Step 2: Make executable and run**

```bash
chmod +x tests/e2e/ralph-codex-e2e/run-tests.sh
bash tests/e2e/ralph-codex-e2e/run-tests.sh
```

Expected output:
```
Checking prerequisites...
Prerequisites OK

========================================
Scenario: happy-path
========================================
Reset complete: happy-path stub restored
Pre-condition check: verifying stub fails tests...
  PRE-CONDITION PASS: stub correctly fails tests
Verifying reset.sh...
  RESET PASS: reset.sh outputs expected message
  Infrastructure verified for: happy-path
  ...

RESULTS
  PASS (pre-conditions): happy-path
  PASS (pre-conditions): unit-retry
  PASS (pre-conditions): e2e-retry
  PASS (pre-conditions): exhaustion

Passed: 4 / 4
```

**Step 3: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/run-tests.sh
git commit -m "test: add run-tests.sh for ralph-codex-e2e integration suite"
```

---

## Task 6: Write skill document test baseline scenarios

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| S1–S6, S4b | All skill document scenarios | skill-tests-delta.md |

**Files:**
- Create: `tests/skills/ralph-codex-e2e-baseline.md`

**Step 1: Write the baseline scenario document**

`tests/skills/ralph-codex-e2e-baseline.md`:
```markdown
# Ralph-Codex-E2E Skill — Baseline Scenarios (No Skill Loaded)

Run each scenario with a subagent that does NOT have the ralph-codex-e2e skill loaded.
Document the exact behavior observed verbatim.

---

## S1: Ralph Loop Command Construction

**Prompt to subagent:**
> "I want to start the Ralph-Codex-E2E workflow for plan at docs/plans/2026-03-02-ralph-codex-e2e-testing.md. Please show me the exact command to run."

**What to observe:**
- Does the agent produce a `/ralph-loop` command?
- Does it include `--max-iterations`?
- Does it include `--completion-promise "DONE"`?
- Does it include per-task Codex phase steps (implement, unit tests, integration tests)?
- Does it include per-task Claude E2E phase steps?

**Baseline behavior (fill in after running):**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S2: Prerequisites Verification

**Prompt to subagent:**
> "I want to run the Ralph-Codex-E2E workflow. ~/.codex/config.toml does not exist on this machine. What should I do?"

**What to observe:**
- Does the agent identify the missing config as a blocker?
- Does it provide the exact fix (`~/.codex/config.toml` with `[sandbox_workspace_write] network_access = true`)?
- Does it instruct the user to configure before proceeding?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S3: When-Not-To-Use Routing

**Prompt to subagent:**
> "I want to execute my implementation plan, but I need to review the code between each task. Should I use Ralph-Codex-E2E?"

**What to observe:**
- Does the agent redirect to `codex-subagent-driven-development`?
- Does it explain why ralph-codex-e2e is wrong here?
- Does it proceed with Ralph loop anyway?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S4: E2E Strategy Detection (Playwright)

**Prompt to subagent:**
> "I'm running the E2E phase of Ralph-Codex-E2E on a project. The project root contains playwright.config.ts. What E2E command should I run?"

**What to observe:**
- Does the agent select `npx playwright test`?
- Or does it default to bash?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S4b: E2E Strategy Detection (API)

**Prompt to subagent:**
> "I'm running the E2E phase on a project that has openapi.yaml but no playwright.config.ts or cypress.config.ts. What E2E strategy should I use?"

**What to observe:**
- Does the agent select API E2E (curl/httpie)?
- Or does it default to bash?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S5: Retry Chain Escalation

**Prompt to subagent:**
> "I'm running Ralph-Codex-E2E. The E2E tests have failed twice. I retried twice as Claude. They still fail. What should I do next?"

**What to observe:**
- Does the agent let Ralph loop again (correct)?
- Does it commit with failing tests (wrong)?
- Does it declare success (wrong)?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]

---

## S6: Post-Loop Verification Steps

**Prompt to subagent:**
> "Ralph has just exited and printed DONE. The project has a docs/specs/my-feature/ directory. What should I do next?"

**What to observe:**
- Does the agent run `superpowers:verify-specs` first?
- Does it then run `superpowers:finishing-a-development-branch`?
- Does it skip either step?

**Baseline behavior:**
[DOCUMENT VERBATIM RESPONSE HERE]
```

**Step 2: Commit**

```bash
git add tests/skills/ralph-codex-e2e-baseline.md
git commit -m "test: add skill document baseline scenario prompts for ralph-codex-e2e"
```
