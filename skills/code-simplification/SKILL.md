---
name: code-simplification
description: Use when Claude dispatches a technical debt cleanup task and you need Codex to remove debt, run scoped static analysis, and refactor safely from a `technical-debt.md` file
---

# Code Simplification

Execute the Codex side of technical debt cleanup: parse the debt file, remove obsolete code safely, then perform narrow static analysis and small refactors.

**Core principle:** Make one small change at a time, run the build command before the test command after every change, and stop Phase 1 immediately if debt removal breaks the build or tests.

**Announce at start:** "I'm using the code-simplification skill to remove technical debt safely."

## Inputs

This skill activates from a dispatch prompt like:

```text
Use superpowerwithcodex:code-simplification

Technical debt file: docs/specs/<feature>/technical-debt.md
Implementation directory: src/
Tests directory: tests/
```

Read `technical-debt.md` and extract:
- Build command
- Test command
- Every `DEBT-N` entry
- The `What`, `Why`, `Replaced by`, `Verification`, and `Source` fields for each debt item

## Phase 1: Debt Removal

Process each debt item sequentially.

For each `DEBT-N`:

1. Remove the obsolete files or code described in `What`
2. Run the build command
3. Run the test command
4. If both pass:
   - mark the item done in `debt-removal-progress.md`
   - commit with message `Remove DEBT-N: <why>`
5. If the build fails:
   - Build output is captured in `debt-removal-progress.md`
   - mark that debt item as failed
   - stop and return
6. If the tests fail:
   - Test output is captured in `debt-removal-progress.md`
   - mark that debt item as failed
   - stop and return

**Rule:** No further debt items are processed after a Phase 1 failure. Static analysis and refactoring are skipped.

### `debt-removal-progress.md`

Write the file with:
- Progress section
- checklist of debt items with done/failed status
- Issues section with any build or test output
- Commits section listing commit SHAs for successful removals

## Phase 2: Scoped Static Analysis

Start Phase 2 only if all Phase 1 debt items succeeded.

Determine analysis scope from:
- Files mentioned in technical-debt.md "What" fields
- Files modified during Phase 1

Do not scan the entire repo for removal candidates unless a scoped file depends on it. This phase is feature-scoped only.

Within scope, scan for:
- unused imports
- unused functions
- unused classes

### Safe Removals

When unused code is safe to remove because it is not referenced anywhere:

1. Remove the unused code
2. Run the build command
3. Run the test command
4. If both pass:
   - update `static-analysis-report.md`
   - commit the removal
5. If either fails:
   - revert that removal
   - document the issue in `static-analysis-report.md`
   - continue to the next unused item

### `static-analysis-report.md`

Write the file with:
- Unused imports section with counts
- Unused functions section with file paths and line numbers
- Unused classes section with details
- Summary section with total lines deleted and counts by category

## Phase 3: Refactoring

Start Phase 3 only after static analysis completes.

Attempt small, high-value refactors in priority order:

1. **Extract duplicate code blocks**
   - Find duplicates of 3+ lines with 2+ occurrences
   - Extract into a shared function
   - Run build command
   - Run test command
   - If both pass: record in `refactor-progress.md` and commit `Extract duplicate: <function_name>`
   - If either fails: revert, skip, continue

2. **Reduce cyclomatic complexity**
   - Target functions with cyclomatic complexity > 10
   - Simplify conditionals or extract subfunctions
   - Run build + test
   - If both pass: record in `refactor-progress.md` and commit `Reduce complexity in <function_name>`
   - If either fails: revert, skip, continue

3. **Apply design patterns**
   - Only when there is obvious value
   - Strategy, factory, or similar patterns are acceptable if they simplify the code
   - Run build + test
   - If both pass: record in `refactor-progress.md` and commit `Apply <pattern> to <component>`
   - If either fails: revert, skip, continue

### Refactoring Failure Rule

If one refactoring attempt fails:
- that refactoring is reverted and skipped
- Subsequent refactorings are attempted
- the final report includes both successful and skipped refactorings

### `refactor-progress.md`

Write the file with:
- list of refactorings applied
- type (`duplicate`, `complexity`, `pattern`)
- location
- rationale
- commit SHA

## Build And Test Rules

- Always execute the build command before the test command after any change
- Support compiled build commands such as `mvn clean compile`
- The build command may do compilation, type-checking, or bundling before tests

## Return Summary To Claude

When all phases complete, or Phase 1 fails, return:

```text
Completed:
- Removed N debt items (X lines deleted)
- Static analysis: Y unused items removed
- Refactored: Z improvements applied

See progress files:
- debt-removal-progress.md
- static-analysis-report.md
- refactor-progress.md
```

## Key Principles

- **Parse the contract first** — `technical-debt.md` is the source of truth
- **Delete in small steps** — one debt item at a time
- **Stop hard on removal failures** — broken cleanup is worse than tracked cleanup
- **Scope analysis narrowly** — only feature-touched files
- **Continue selective refactoring** — revert individual failures, keep successful improvements

## Integration

**Called by:**
- `superpowers:cleanup-and-refactor`

**Produces:**
- `debt-removal-progress.md`
- `static-analysis-report.md`
- `refactor-progress.md`

**Returns:**
- A completion summary for Claude/orchestrator
