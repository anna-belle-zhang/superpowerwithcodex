# Cleanup and Refactor - Living Spec

## Behaviors

### Validate technical debt file exists
GIVEN user invokes cleanup-and-refactor with a feature name
WHEN the skill runs Step 1 (validation)
THEN it confirms `docs/specs/<feature>/technical-debt.md` exists, otherwise errors with "No technical debt file found for <feature>"

*Added: 2026-03-12 via technical-debt-cleanup*

### Validate base branch is clean
GIVEN cleanup-and-refactor is invoked
WHEN the skill runs Step 1 (validation)
THEN it confirms no uncommitted changes in the base branch, otherwise errors with "Base branch has uncommitted changes"

*Added: 2026-03-12 via technical-debt-cleanup*

### Create isolated worktree
GIVEN validation passes
WHEN the skill runs Step 2 (create worktree)
THEN a git worktree is created on branch `cleanup/<feature>` using the `using-git-worktrees` pattern

*Added: 2026-03-12 via technical-debt-cleanup*

### Update project-level debt status to In Progress
GIVEN worktree is created
WHEN the skill runs Step 3 (update status)
THEN `docs/specs/_technical-debt.md` is updated:
- All debt items for this feature set status to "In Progress"
- Start timestamp is recorded

*Added: 2026-03-12 via technical-debt-cleanup*

### Dispatch Codex with debt file path
GIVEN worktree exists and status is updated
WHEN the skill runs Step 4 (dispatch)
THEN Codex is dispatched via MCP with prompt:
```
Use superpowerwithcodex:code-simplification

Technical debt file: docs/specs/<feature>/technical-debt.md
Implementation directory: src/
Tests directory: tests/
```

*Added: 2026-03-12 via technical-debt-cleanup*

### Run automated verification after Codex returns
GIVEN Codex completes and returns
WHEN the skill runs Step 5 (verification)
THEN the following commands are executed in sequence:
1. Build command from technical-debt.md
2. Test command from technical-debt.md
3. Optional static checks (if configured)

*Added: 2026-03-12 via technical-debt-cleanup*

### Present merge options on verification success
GIVEN automated verification passes (build + test green)
WHEN the skill runs Step 6 (present options)
THEN the user is shown:
```
✅ All verification passed
Choose merge strategy:
A) Auto-merge to main
B) Create PR for review
C) Manual review - show diff
D) Abort - keep worktree
```

*Added: 2026-03-12 via technical-debt-cleanup*

### Auto-merge to main branch
GIVEN user chooses option A (auto-merge)
AND main branch is clean
WHEN the skill runs Step 7 (execute merge)
THEN the cleanup branch is merged to main and pushed

*Added: 2026-03-12 via technical-debt-cleanup*

### Create PR for review
GIVEN user chooses option B (create PR)
WHEN the skill runs Step 7 (execute merge)
THEN a pull request is created using `gh pr create` with title "Clean up technical debt: <feature>"

*Added: 2026-03-12 via technical-debt-cleanup*

### Show diff for manual review
GIVEN user chooses option C (manual review)
WHEN the skill runs Step 7 (execute merge)
THEN `git diff main...cleanup/<feature>` output is shown and the skill waits for user commands

*Added: 2026-03-12 via technical-debt-cleanup*

### Abort and keep worktree
GIVEN user chooses option D (abort)
WHEN the skill runs Step 7 (execute merge)
THEN the worktree path is printed and the skill exits without merging

*Added: 2026-03-12 via technical-debt-cleanup*

### Update project-level debt status to Completed
GIVEN merge completes successfully (option A or B)
WHEN the skill runs Step 7 (update status)
THEN `docs/specs/_technical-debt.md` is updated:
- All debt items for this feature set status to "Completed"
- Completion timestamp is recorded
- Summary from progress files is added as notes

*Added: 2026-03-12 via technical-debt-cleanup*

### Update project-level debt status to Failed
GIVEN verification fails OR user aborts
WHEN the skill runs Step 7 (update status)
THEN `docs/specs/_technical-debt.md` is updated:
- All debt items for this feature set status to "Failed"
- Error details or abort reason is recorded

*Added: 2026-03-12 via technical-debt-cleanup*

### Handle build failure during verification
GIVEN build command fails during Step 5
WHEN the skill handles the error
THEN build output is shown and user is prompted:
- Retry verification
- Manual fix (show worktree path)
- Abort (update status to Failed)

*Added: 2026-03-12 via technical-debt-cleanup*

### Handle test failure during verification
GIVEN test command fails during Step 5
WHEN the skill handles the error
THEN test output is shown and user is prompted:
- Retry verification
- Manual fix (show worktree path)
- Abort (update status to Failed)

*Added: 2026-03-12 via technical-debt-cleanup*

### Handle auto-merge conflict
GIVEN user chooses auto-merge
AND merge conflicts occur
WHEN the skill executes the merge
THEN it falls back to creating a PR instead and notifies the user

*Added: 2026-03-12 via technical-debt-cleanup*

### Handle worktree already exists
GIVEN a worktree for `cleanup/<feature>` already exists
WHEN the skill runs Step 2 (create worktree)
THEN user is prompted: "Worktree already exists. Delete and retry? (yes/no)"

*Added: 2026-03-12 via technical-debt-cleanup*
