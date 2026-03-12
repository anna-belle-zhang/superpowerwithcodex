---
name: cleanup-and-refactor
description: Use when a feature has a `technical-debt.md` file and you need to orchestrate safe cleanup in an isolated worktree before merge
---

# Cleanup And Refactor

Coordinate technical debt cleanup safely from the Claude/orchestrator side.

**Core principle:** Validate first, isolate risky changes in a worktree, verify build and tests after Codex returns, then let the user choose how to integrate.

**Announce at start:** "I'm using the cleanup-and-refactor skill to orchestrate technical debt cleanup."

## Overview

This skill owns the outer workflow:
1. Validate inputs and branch cleanliness
2. Create or reuse an isolated worktree on `cleanup/<feature>`
3. Update `docs/specs/_technical-debt.md` to `In Progress`
4. Dispatch Codex with `superpowerwithcodex:code-simplification`
5. Run automated verification using the build and test commands from `technical-debt.md`
6. Present merge options
7. Update debt status to `Completed` or `Failed`

## The Process

### Step 1: Validate Prerequisites

Confirm the feature-level debt file exists:

```bash
test -f "docs/specs/<feature>/technical-debt.md"
```

If not, stop with:

```text
No technical debt file found for <feature>
```

Confirm the base branch is clean before creating the cleanup branch:

```bash
git diff --quiet
git diff --cached --quiet
```

If the base branch has changes, stop with:

```text
Base branch has uncommitted changes
```

### Step 2: Create Isolated Worktree

Follow the `superpowers:using-git-worktrees` pattern.

Target branch name:

```text
cleanup/<feature>
```

If a worktree for `cleanup/<feature>` already exists, prompt:

```text
Worktree already exists. Delete and retry? (yes/no)
```

Create the worktree using the repo's normal worktree location rules, then switch into that worktree before dispatching Codex.

### Step 3: Update Debt Tracker to In Progress

Update `docs/specs/_technical-debt.md`:
- Set all debt items for the feature to `In Progress`
- Record a start timestamp
- Note the cleanup branch/worktree path

### Step 4: Dispatch Codex

Send Codex a prompt that includes the exact skill activation and the technical debt file path:

```text
Use superpowerwithcodex:code-simplification

Technical debt file: docs/specs/<feature>/technical-debt.md
Implementation directory: src/
Tests directory: tests/
```

Codex is expected to:
- read `technical-debt.md`
- remove debt items sequentially
- run static analysis in feature scope only
- attempt targeted refactors
- write `debt-removal-progress.md`, `static-analysis-report.md`, and `refactor-progress.md`

### Step 5: Run Automated Verification

After Codex returns, execute verification in this sequence:

1. Build command from technical-debt.md
2. Test command from technical-debt.md
3. Optional static checks, if the project or debt file defines them

Always run the build command before the test command.

### Step 5a: Handle Verification Failure

If the build command fails during verification:
- show the build output
- update `docs/specs/_technical-debt.md` to `Failed`
- prompt:

```text
Retry verification
Manual fix (show worktree path)
Abort
```

If the test command fails during verification:
- show the test output
- update `docs/specs/_technical-debt.md` to `Failed`
- prompt:

```text
Retry verification
Manual fix (show worktree path)
Abort
```

If the user chooses manual fix, print the worktree path and stop.
If the user chooses abort, keep the worktree and record the abort reason as `Failed`.

### Step 6: Present Merge Options

When verification passes, show:

```text
✅ All verification passed
Choose merge strategy:
A) Auto-merge to main
B) Create PR for review
C) Manual review - show diff
D) Abort - keep worktree
```

### Step 7: Execute the Chosen Merge Path

#### Option A: Auto-merge to main

Before merging, confirm `main` is clean.

If merge succeeds:
- merge `cleanup/<feature>` to `main`
- push if appropriate for the repo
- update `docs/specs/_technical-debt.md` to `Completed`

If merge conflicts occur:
- fall back to creating a PR instead
- notify the user that auto-merge could not complete and a PR is being created

#### Option B: Create PR for review

Create the PR with GitHub CLI:

```bash
gh pr create --title "Clean up technical debt: <feature>"
```

Then update `docs/specs/_technical-debt.md` to `Completed`.

#### Option C: Manual review - show diff

Show:

```bash
git diff main...cleanup/<feature>
```

Wait for further user instructions. Do not merge automatically.

#### Option D: Abort - keep worktree

Print the worktree path and exit without merging. Mark the debt tracker entry as `Failed` with the abort reason.

### Step 7a: Update Final Debt Status

On successful merge or PR creation:
- set feature debt items to `Completed`
- record completion timestamp
- copy in summary notes from:
  - `debt-removal-progress.md`
  - `static-analysis-report.md`
  - `refactor-progress.md`

On verification failure or user abort:
- set feature debt items to `Failed`
- record the error details or abort reason

## Output Expectations

Successful completion should leave:
- `docs/specs/_technical-debt.md` updated to `Completed`
- progress/report files written in the feature worktree
- either a merged branch, an open PR, or a shown diff for manual review

Failure should leave:
- the worktree intact for debugging
- `docs/specs/_technical-debt.md` updated to `Failed`
- the last build/test output visible to the user

## Key Principles

- **Validate before worktree creation** — avoid isolating a broken starting state
- **Use worktree isolation** — cleanup is risky and should not mutate the main workspace
- **Build before test** — compiled projects need this order
- **Status must be explicit** — `Pending` → `In Progress` → `Completed` or `Failed`
- **Manual review stays available** — cleanup is not a forced auto-merge

## Integration

**Called by:**
- `superpowers:verifying-specs` — when debt is found and the user chooses cleanup
- Manual invocation via `/superpowerwithcodex:cleanup-and-refactor`

**Uses:**
- `superpowers:using-git-worktrees` for safe worktree setup
- `superpowerwithcodex:code-simplification` for Codex execution

**Produces:**
- Updated `docs/specs/_technical-debt.md`
- Verification output and merge-choice prompt
