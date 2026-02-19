---
name: verifying-specs
description: Use when implementation is complete and you need to verify all GIVEN/WHEN/THEN scenarios have corresponding tests - checks completeness, correctness, and coherence of specs against implementation
---

# Verifying Specifications

Verify that implementation fully satisfies structured specifications before merge.

**Core principle:** Every GIVEN/WHEN/THEN scenario must have a passing test. No exceptions.

**Announce at start:** "I'm using the verifying-specs skill to verify specifications."

## Overview

Three verification checks:
1. **Completeness** — every scenario has a corresponding test
2. **Correctness** — each test's setup/action/assertion matches its scenario
3. **Coherence** — no contradictions between deltas or against living specs

## The Process

### Step 1: Locate Specs

- Find the feature specs directory: `docs/specs/<feature>/`
- Read all `*-delta.md` files in `docs/specs/<feature>/specs/`
- If no specs directory exists: "No structured specs found. Skipping verification."
- Extract every GIVEN/WHEN/THEN scenario into a checklist.

### Step 2: Completeness Check

For each scenario in the delta specs:

1. Search the test files for a test that covers this scenario
2. Match by behavior, not by name (a test named differently but covering the scenario counts)
3. Mark each scenario: COVERED or MISSING

**Output format:**

```markdown
## Completeness Report

| Scenario | Source | Status | Test |
|----------|--------|--------|------|
| GIVEN x WHEN y THEN z | auth-delta.md | COVERED | test_login_success |
| GIVEN a WHEN b THEN c | auth-delta.md | MISSING | - |

**Coverage: N/M scenarios covered (X%)**
```

**If any MISSING:** Report as blocking issue. Cannot proceed.

### Step 3: Correctness Check

For each COVERED scenario, verify the test actually matches:

1. **Setup matches GIVEN** — test preconditions align with scenario preconditions
2. **Action matches WHEN** — test action aligns with scenario action
3. **Assertion matches THEN** — test assertion verifies the scenario's expected outcome

**Output format:**

```markdown
## Correctness Report

| Scenario | Test | Setup | Action | Assertion | Status |
|----------|------|-------|--------|-----------|--------|
| GIVEN x WHEN y THEN z | test_login | OK | OK | OK | CORRECT |
| GIVEN a WHEN b THEN c | test_auth | OK | MISMATCH | OK | INCORRECT |

**Correctness: N/M tests correct (X%)**
```

**If any INCORRECT:** Report the mismatch with specifics. Blocking issue.

### Step 4: Coherence Check

Check for contradictions:

1. **Between deltas:** No two delta specs define contradictory behavior for the same component
2. **Against living specs:** MODIFIED entries in deltas correctly reference what exists in `docs/specs/_living/`
3. **REMOVED entries:** Items marked REMOVED actually exist in living specs

**Output format:**

```markdown
## Coherence Report

- No contradictions between delta specs: OK/FAIL
- Delta MODIFIED entries match living specs: OK/FAIL/N/A (no living specs)
- Delta REMOVED entries exist in living specs: OK/FAIL/N/A (no removals)

**Coherence: PASS/FAIL**
```

### Step 5: Final Verdict

```markdown
## Verification Summary

| Check | Result |
|-------|--------|
| Completeness | PASS/FAIL (N/M covered) |
| Correctness | PASS/FAIL (N/M correct) |
| Coherence | PASS/FAIL |

**Overall: PASS/FAIL**
```

**If FAIL:** List all blocking issues. Do not proceed with merge/finish.

**If PASS:** "All specifications verified. Safe to proceed with merge/finish."

## Blocking Rules

- **Any MISSING scenario** → FAIL (must write test first)
- **Any INCORRECT test** → FAIL (must fix test or update spec)
- **Any contradiction** → FAIL (must resolve before proceeding)
- **All checks pass** → PASS (proceed to archiving)

## Key Principles

- **Scenarios are contracts** — a missing test is a broken contract
- **Match by behavior, not name** — test naming conventions vary
- **Read the actual test code** — don't just check for test existence
- **Report specifics** — "MISSING" alone isn't helpful; say which scenario and what's needed
- **Block on failure** — verification gates the merge, no exceptions

## Integration

**Called by:**
- `superpowers:finishing-a-development-branch` — Step 1b before merge options
- `superpowers:ralph-codex-e2e` — post-loop before cleanup

**Requires:**
- Delta specs in `docs/specs/<feature>/specs/`
- Implemented and passing tests

**Followed by:**
- `superpowers:archiving-specs` — after verification passes
