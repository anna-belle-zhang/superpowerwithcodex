---
description: Verify all spec scenarios have corresponding tests
---

# Verifying Specifications

Verify that implementation fully satisfies structured specifications before merge, then capture any technical debt surfaced by the change.

**Core principle:** Every GIVEN/WHEN/THEN scenario must have a passing test. No exceptions.

**Announce at start:** "I'm using the verifying-specs skill to verify specifications."

## Overview

Three blocking verification checks:
1. **Completeness** — every scenario has a corresponding test
2. **Correctness** — each test's setup/action/assertion matches its scenario
3. **Coherence** — no contradictions between deltas or against living specs

Technical debt follow-up:
4. **Debt identification** — collect `// DEBT:` annotations and behaviors replaced by REMOVED deltas
5. **Debt tracking** — write `technical-debt.md`, update `_technical-debt.md`, and offer cleanup

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

### Step 4a: Collect Manual Debt Annotations

Scan the codebase for `// DEBT:` comments after verification passes:

```bash
rg -n "// DEBT:" src tests . 2>/dev/null
```

If no manual annotations and no REMOVED scenarios: skip to Step 5.

### Step 4b: Scenario-Driven Debt Identification

When delta specs contain `## REMOVED`, compare against `docs/specs/_living/`:

1. Read the REMOVED behaviors in each delta
2. Search `_living/` for matching behavior headings or scenario text
3. Treat matching living behaviors as technical debt to remove from code/docs

### Step 4c: Write Feature-Level `technical-debt.md`

When debt items are identified, write `docs/specs/<feature>/technical-debt.md`:

```markdown
# Technical Debt

## Build Commands
**Build command:** <build command>
**Test command:** <test command>

## Technical Debt

### DEBT-N: <short label>
**What:** <files or obsolete behavior to remove>
**Why:** <reason this is debt>
**Replaced by:** <new implementation or scenario>
**Verification:** <how to verify removal>
**Source:** <manual annotation or living/delta reference>
```

### Step 4d: Update Project-Level Debt Tracker

Create or update `docs/specs/_technical-debt.md` with one row per debt item (unique DEBT-N IDs, feature name, file paths, priority, status: Pending).

### Step 4e: Prompt for Cleanup

If debt items were found:

```text
Found N debt items. Run cleanup-and-refactor now? (yes/no)
```

- If yes: invoke `superpowers:cleanup-and-refactor`
- If no: continue to `superpowers:archiving-specs`

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

- **Any MISSING scenario** → FAIL
- **Any INCORRECT test** → FAIL
- **Any contradiction** → FAIL
- **Debt found** → track it, but do not fail verification solely for tracked debt
- **All checks pass** → PASS
