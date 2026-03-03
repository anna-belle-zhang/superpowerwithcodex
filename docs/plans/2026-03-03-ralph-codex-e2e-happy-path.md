# Ralph Codex E2E Happy Path Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a minimal "happy-path" toy Node.js project used by ralph-codex-e2e to practice plan execution (stub stays broken so tests fail).

**Architecture:** Standalone npm package under `tests/e2e/ralph-codex-e2e/happy-path` with a stubbed `greet` function, tests that expect real output, helper scripts for e2e and reset. No runtime wiring beyond the local folder.

**Tech Stack:** Node.js (node:test, assert), npm scripts, bash.

---

### Task 1: Scaffold happy-path project files

**Files:**
- Create: `tests/e2e/ralph-codex-e2e/happy-path/package.json`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/src/greet.js`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/src/greet.js.stub`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/tests/greet.test.js`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/tests/e2e.sh`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/plan.md`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/expected-outcome.md`
- Create: `tests/e2e/ralph-codex-e2e/happy-path/reset.sh`

**Step 1: Write package manifest**

```json
{
  "name": "happy-path",
  "version": "1.0.0",
  "scripts": {
    "test": "node --test tests/greet.test.js"
  }
}
```

**Step 2: Add stubbed greet implementation**

Create `src/greet.js` and `src/greet.js.stub` with:

```js
function greet(name) {
  throw new Error('Not implemented');
}
module.exports = { greet };
```

**Step 3: Add tests that expect real output**

`tests/greet.test.js`:

```js
const { describe, it } = require('node:test');
const assert = require('node:assert');
const { greet } = require('../src/greet');

describe('greet', () => {
  it('returns Hello, World! when given World', () => {
    assert.strictEqual(greet('World'), 'Hello, World!');
  });
  it('returns Hello, Alice! when given Alice', () => {
    assert.strictEqual(greet('Alice'), 'Hello, Alice!');
  });
});
```

**Step 4: Add e2e runner**

`tests/e2e.sh`:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
npm test
echo "E2E PASSED"
```

**Step 5: Add plan and expected outcome docs**

`plan.md` and `expected-outcome.md` per spec (outline behavior and success criteria).

**Step 6: Add reset helper**

`reset.sh`:

```bash
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/src/greet.js.stub" "$SCRIPT_DIR/src/greet.js"
echo "Reset complete: happy-path stub restored"
```

---

### Task 2: Install dependencies and verify failing tests

**Files:** None

**Step 1: Install**

Run inside `tests/e2e/ralph-codex-e2e/happy-path`:

```bash
npm install
```

**Step 2: Run tests (should fail)**

```bash
npm test
```

Expected: Tests fail with "Not implemented" error because stub throws.

**Step 3: Run reset helper**

```bash
bash reset.sh
```

Expected: Output `Reset complete: happy-path stub restored`.

---

### Task 3: Permissions and commit

**Files:**
- Modify: `tests/e2e/ralph-codex-e2e/happy-path/tests/e2e.sh` (chmod)
- Modify: `tests/e2e/ralph-codex-e2e/happy-path/reset.sh` (chmod)

**Step 1: Make helper scripts executable**

```bash
chmod +x tests/e2e/ralph-codex-e2e/happy-path/reset.sh tests/e2e/ralph-codex-e2e/happy-path/tests/e2e.sh
```

**Step 2: Commit**

```bash
git add tests/e2e/ralph-codex-e2e/happy-path/
git commit -m "test: add happy-path toy project for ralph-codex-e2e"
```

Expected: Commit contains new happy-path project with stubbed greet and failing tests.

