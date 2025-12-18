# Test Codex Integration - Simple Feature

---
execution-strategy: codex-subagents
created: 2025-12-18
---

**Goal:** Validate `superpowers:codex-subagent-driven-development` end-to-end with a tiny math utility feature.

## Task 1: Add `sum()` Utility Function

**Files:**
- Create: `src/utils/math.js`
- Test: `tests/utils/math.test.js`

**Step 1: Write failing test**

```javascript
const { sum } = require('../../src/utils/math');

test('sum adds two numbers', () => {
  expect(sum(2, 3)).toBe(5);
});
```

**Step 2: Run test to verify it fails**

Run: `npm test tests/utils/math.test.js`
Expected: FAIL - `sum` not defined / module not found

**Step 3: Implement via Codex**

Dispatch Codex with explicit file boundaries:
- Implement in: `src/utils/math.js`
- Read only: `tests/utils/math.test.js`, `package.json`, lockfiles

Target implementation:

```javascript
function sum(a, b) {
  return a + b;
}

module.exports = { sum };
```

**Step 4: Run test to verify it passes**

Run: `npm test tests/utils/math.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add src/utils/math.js tests/utils/math.test.js
git commit -m "feat: add sum utility function"
```

## Manual Verification Checklist

1. Verify Codex availability (MCP config + `codex` CLI).
2. Run Task 1 using `superpowers:codex-subagent-driven-development`.
3. Confirm:
   - tests are written by Claude first
   - Codex only edits allowed files
   - tests pass before committing implementation
4. Verify git history is clean and messages are readable.

