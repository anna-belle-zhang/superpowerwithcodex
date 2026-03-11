# Technical Debt Cleanup & Refactoring Design

**Date:** 2026-03-11
**Status:** Design Complete — Ready for Specs

---

## 1. Overview & Motivation

**Problem:** Technical debt accumulates during feature development - old code gets replaced but not removed, creating maintenance burden and potential bugs. The spec-driven workflow validates new behavior but doesn't systematically identify or remove obsolete code.

**Solution:** Extend the specs workflow with technical debt tracking and systematic cleanup. During `verify-specs`, both manual annotations (`// DEBT:` comments) and scenario-driven analysis (comparing `_living/` specs to REMOVED sections in delta specs) identify debt. A new skill pair handles removal: Claude's `cleanup-and-refactor` orchestrates via worktree isolation, while Codex's `code-simplification` executes debt removal, static analysis for unused code, and targeted refactoring.

**Key Benefits:**
- Debt is tracked explicitly, not forgotten
- Safe removal through worktree isolation + automated verification
- Refactoring happens at the right time (after debt removal, while context is fresh)
- Rollback capability if cleanup breaks the system

---

## 2. Technical Debt Tracking

**Two-Phase Identification:**
1. **During implementation:** Developers add `// DEBT: <reason>` comments when they notice code that should be removed
2. **At verify-specs time:** Scenario-driven analysis compares `docs/specs/_living/` (current system behaviors) against REMOVED sections in delta specs - any living scenario marked REMOVED indicates debt

**Two-Level Tracking:**
- **Feature-level:** `docs/specs/<feature>/technical-debt.md` contains structured entries (What, Why, Replaced by, Verification, Source) plus build/test commands
- **Project-level:** `docs/specs/_technical-debt.md` maintains aggregated table (ID, Feature, Files, Status, Priority) across all features

**Feature-Level Structure:**
```markdown
## Build Commands
**Build command:** `mvn clean compile`
**Test command:** `mvn test`

## Technical Debt

### DEBT-1: Remove old service
**What:** `src/old_service.py` and tests
**Why:** Superseded by new architecture
**Replaced by:** `src/new_service.py`
**Verification:** Run `mvn test` - all pass
**Source:** Scenario-driven (living:old-service.md → REMOVED)

### DEBT-2: Remove legacy auth
**What:** `src/legacy_auth.py:L45-120`
**Why:** Old auth, remove after OAuth migration
**Replaced by:** `src/oauth_provider.py`
**Verification:** Run `npm test` and manual auth test
**Source:** Manual annotation (`// DEBT:` comment at src/legacy_auth.py:L45)
```

**Project-Level Structure:**
```markdown
# Project Technical Debt

| ID | Feature | Files | Status | Priority |
|---|---|---|---|---|
| DEBT-1 | skill-marketplace | ado_dump.py | Completed | High |
| DEBT-2 | oauth-migration | legacy_auth.py | In Progress | Medium |
| DEBT-3 | api-v2 | legacy_endpoint.py | Pending | Low |
```

**Updates:**
- `verify-specs` creates/updates both files when debt is identified (status: Pending)
- `cleanup-and-refactor` updates status during execution (In Progress → Completed/Failed)

---

## 3. Skill Architecture

**Skill Pair Pattern:** Following the Claude-Codex specs-tdd model, we create two skills in the same repo:

### Claude Skill: `skills/cleanup-and-refactor/SKILL.md`

**Responsibilities:**
- Orchestrates the cleanup workflow
- Creates worktree on cleanup branch for isolation
- Dispatches Codex via MCP with technical-debt.md path
- Runs automated verification (build + test + static checks)
- Presents merge options if verification passes
- Updates project-level `_technical-debt.md` with status changes

**Entry Mode:**
- Typically invoked after `verify-specs` identifies debt
- Can be invoked manually later with feature name

**Dispatch Prompt to Codex:**
```
Use superpowerwithcodex:code-simplification

Technical debt file: docs/specs/<feature>/technical-debt.md
Implementation directory: src/
Tests directory: tests/
```

### Codex Skill: `skills/code-simplification/SKILL.md`

**Responsibilities:**
- Activated when dispatched by Claude
- **Phase 1:** Remove debt items from technical-debt.md sequentially
- **Phase 2:** Static analysis to find unused functions/classes/imports
- **Phase 3:** Refactor remaining code (prioritized: duplicates → complexity → patterns)
- Handles build steps (uses build command from technical-debt.md)
- Runs tests after each removal
- Writes three progress files

**Process:**

1. **Read technical-debt.md** - parse build commands and debt items
2. **Phase 1: Debt Removal**
   - For each DEBT-N entry:
     - Remove files/code specified in "What"
     - Run build command
     - Run test command
     - If tests pass: mark done in `debt-removal-progress.md`, commit
     - If tests fail: document issue, stop
3. **Phase 2: Static Analysis**
   - Scan for unused imports, functions, classes
   - Write findings to `static-analysis-report.md`
   - Remove safe unused code (not referenced anywhere)
   - Test after each removal
4. **Phase 3: Refactoring**
   - **Priority 1:** Extract duplicated code into shared functions
   - **Priority 2:** Simplify complex conditionals (reduce cyclomatic complexity)
   - **Priority 3:** Apply design patterns where clear value
   - Test after each refactoring
   - Document changes in `refactor-progress.md`

**Progress Files:**
```
docs/specs/<feature>/
  debt-removal-progress.md       # Checklist of debt items with status
  static-analysis-report.md      # Unused code findings and actions
  refactor-progress.md           # Refactorings applied with rationale
```

**Installation:** Both skills discovered automatically when superpowerwithcodex plugin is installed - Claude Code finds Claude skills, Codex finds Codex skills via `~/.codex/superpowerwithcodex/skills/`.

---

## 4. Workflow Integration

**Enhanced Workflow Chain:**
```
brainstorm → write-specs → worktree → write-plan → execute
  ↓
verify-specs (ENHANCED: after completeness/correctness/coherence checks)
  - Collect // DEBT: comments from codebase
  - Compare _living/ specs to REMOVED sections in delta specs
  - Write feature-level technical-debt.md
  - Update project-level _technical-debt.md (status: Pending)
  - Prompt: "Found N debt items. Run cleanup-and-refactor now? (yes/no)"
  ↓
[IF YES] cleanup-and-refactor
  - Create worktree on cleanup/<feature> branch
  - Dispatch Codex: "Use superpowerwithcodex:code-simplification"
  - Wait for Codex completion
  - Run verification: build → test → optional static checks
  - Update _technical-debt.md status
  - Present options: auto-merge | create PR | manual review
  ↓
[IF NO] skip to archive-specs (debt tracked for later)
  ↓
archive-specs → finish
```

**Key Integration Points:**

### verify-specs Enhancement (Step 4: Identify Technical Debt)

After existing checks (completeness, correctness, coherence):

1. **Collect manual annotations:**
   - Grep for `// DEBT:` comments in implementation directories
   - Parse: file path, line number, reason from comment

2. **Scenario-driven analysis:**
   - Read all `docs/specs/_living/*.md` files
   - Read all delta specs `docs/specs/<feature>/specs/*-delta.md`
   - For each REMOVED section: find matching scenarios in living specs
   - Cross-reference: living scenario → implementation files (via test mappings)

3. **Write feature-level technical-debt.md:**
   - Build commands from project config or prompt user
   - Structured entries for each debt item (What, Why, Replaced by, Verification, Source)

4. **Update project-level _technical-debt.md:**
   - Add new entries with status: Pending
   - Generate unique DEBT-N IDs

5. **Prompt user:**
   ```
   ✅ Verification complete
   ⚠️  Found 3 technical debt items:
       - DEBT-1: Remove old_service.py (scenario-driven)
       - DEBT-2: Remove legacy_auth.py:L45-120 (manual annotation)
       - DEBT-3: Remove deprecated endpoint (scenario-driven)

   Run cleanup-and-refactor now? (yes/no)
   ```

### cleanup-and-refactor Workflow

**Entry:**
- Invoked by verify-specs prompt OR
- Manual invocation: `/superpowerwithcodex:cleanup-and-refactor` with feature name

**Process:**

1. **Validate inputs:**
   - Confirm `docs/specs/<feature>/technical-debt.md` exists
   - Confirm base branch is clean (no uncommitted changes)

2. **Create worktree:**
   - Use `superpowerwithcodex:using-git-worktrees` pattern
   - Branch name: `cleanup/<feature>`
   - Location: project-local `.worktrees/` or global config

3. **Update project-level status:**
   - Set status to "In Progress" in `_technical-debt.md`
   - Timestamp: start time

4. **Dispatch Codex:**
   ```
   Use superpowerwithcodex:code-simplification

   Technical debt file: docs/specs/<feature>/technical-debt.md
   Implementation directory: src/
   Tests directory: tests/
   ```

5. **Monitor completion:**
   - Wait for Codex return
   - Read progress files to understand what was done

6. **Automated verification:**
   - Run build command from technical-debt.md
   - Run test command
   - Optional: run linting/type checking

7. **Handle results:**
   - **If verification passes:** Present merge options
   - **If verification fails:** Show errors, offer retry or abort

8. **Present merge options:**
   ```
   ✅ All verification passed:
      - Build: SUCCESS
      - Tests: 42/42 passing
      - Removed: 3 debt items, 127 lines deleted
      - Static analysis: 5 unused functions removed
      - Refactored: 2 duplicates extracted, 1 complexity reduction

   Choose merge strategy:
   A) Auto-merge to main (fast, requires clean main branch)
   B) Create PR for review (recommended for shared repos)
   C) Manual review - show me the diff first
   D) Abort - keep worktree for manual inspection
   ```

9. **Execute merge:**
   - Option A: `git checkout main && git merge cleanup/<feature> && git push`
   - Option B: `gh pr create --title "Clean up technical debt: <feature>"`
   - Option C: Show `git diff main...cleanup/<feature>`, await user command
   - Option D: Print worktree path, exit

10. **Update project-level status:**
    - Set status to "Completed" (if merged) or "Failed" (if aborted)
    - Timestamp: completion time
    - Add notes from progress files

**Key Points:**
- Worktree isolation means main workspace unaffected during cleanup
- Failed cleanup can be abandoned; worktree deleted, no harm done
- All changes are atomic - either full merge or nothing

---

## 5. Verification & Merge

### Automated Verification

After Codex completes, Claude runs:

1. **Build step:**
   - Execute build command from technical-debt.md
   - Handles Java/C++/Go compilation
   - Example: `mvn clean compile` or `cmake . && make`

2. **Test suite:**
   - Run test command - must be 100% green
   - Example: `mvn test` or `npm test`

3. **Optional static checks:**
   - Linting, type checking (project-dependent)
   - Example: `eslint src/` or `mypy .`

### Merge Options

If all verification passes:
```
✅ All verification passed:
   - Build: SUCCESS
   - Tests: 42/42 passing
   - Removed: 3 debt items, 127 lines deleted
   - Refactored: 2 duplicates extracted, 1 complexity reduction

Choose merge strategy:
A) Auto-merge to main (fast, requires clean main branch)
B) Create PR for review (recommended for shared repos)
C) Manual review - show me the diff first
D) Abort - keep worktree for manual inspection
```

### Status Updates

Project-level `_technical-debt.md` updated with:
- **Status changes:**
  - Pending → In Progress (when Codex starts)
  - In Progress → Completed (after successful merge)
  - In Progress → Failed (if verification fails or aborted)
- **Completion date** for audit trail
- **Notes** from progress files (summary of changes)

### Rollback Safety

Worktree isolation means original workspace untouched:
- If cleanup breaks tests → delete worktree, try again
- If cleanup is risky → create PR instead of auto-merge
- If unsure → manual review option shows full diff first

---

## 6. Data Flow & File Locations

### Input Files
```
docs/specs/<feature>/
  technical-debt.md              # Created by verify-specs
  specs/
    <component>-delta.md         # Contains REMOVED sections
docs/specs/_living/
  <component>.md                 # Current system behaviors
src/                             # Contains // DEBT: comments
```

### Output Files (Created by Codex)
```
docs/specs/<feature>/
  debt-removal-progress.md       # Phase 1 progress
  static-analysis-report.md      # Phase 2 findings
  refactor-progress.md           # Phase 3 changes
```

### Tracking Files (Updated by Both)
```
docs/specs/_technical-debt.md    # Project-level aggregation
```

### Sequence Diagram
```
Claude (verify-specs):
  - Collect // DEBT: comments
  - Compare _living/ to REMOVED sections
  → Write technical-debt.md
  → Update _technical-debt.md (Pending)
  → Prompt user

Claude (cleanup-and-refactor):
  - Create worktree
  → Dispatch Codex with technical-debt.md path

  Codex (code-simplification):
    - Read technical-debt.md
    - Phase 1: Remove debt items → debt-removal-progress.md
    - Phase 2: Static analysis → static-analysis-report.md
    - Phase 3: Refactor → refactor-progress.md
    ← Return

  ← Read progress files
  - Run build + test verification
  - Present merge options
  → Update _technical-debt.md (Completed/Failed)
```

---

## 7. Modified Existing Skills

### skills/verifying-specs/SKILL.md

**NEW: Step 4 - Identify Technical Debt**

After existing completeness/correctness/coherence checks:

```markdown
## Step 4: Identify Technical Debt

### 4a. Collect Manual Annotations
- Grep for `// DEBT:` comments in `src/` and `tests/` directories
- Parse: file path, line number, reason

### 4b. Scenario-Driven Analysis
- Read `docs/specs/_living/*.md` (current system behaviors)
- Read delta specs REMOVED sections
- Cross-reference: for each REMOVED scenario, identify implementing code via test mappings

### 4c. Write Feature-Level Debt File
- Create `docs/specs/<feature>/technical-debt.md`
- Prompt for build/test commands if not in project config
- Write structured entries (What, Why, Replaced by, Verification, Source)

### 4d. Update Project-Level Debt Tracker
- Update `docs/specs/_technical-debt.md`
- Add entries with status: Pending
- Generate unique DEBT-N IDs

### 4e. Prompt User
If debt items found:
"Found N technical debt items. Run cleanup-and-refactor now? (yes/no)"
- Yes → invoke cleanup-and-refactor skill
- No → continue to archive-specs
```

---

## 8. New Skills

### skills/cleanup-and-refactor/SKILL.md (Claude)

```markdown
---
name: cleanup-and-refactor
description: Use when verify-specs identifies technical debt - orchestrates systematic removal via Codex in isolated worktree, with automated verification and merge options
---

# Technical Debt Cleanup & Refactoring

## Overview

Orchestrates systematic removal of technical debt identified by verify-specs. Creates isolated worktree, dispatches Codex for cleanup/refactoring, runs automated verification, presents merge options.

## When to Use

- After verify-specs identifies technical debt and prompts user
- Manual invocation when technical-debt.md exists: `/superpowerwithcodex:cleanup-and-refactor <feature>`

## Process

### Step 1: Validate Inputs
- Confirm `docs/specs/<feature>/technical-debt.md` exists
- Confirm base branch clean (no uncommitted changes)

### Step 2: Create Worktree
- Use `superpowerwithcodex:using-git-worktrees` pattern
- Branch: `cleanup/<feature>`

### Step 3: Update Status
- Update `docs/specs/_technical-debt.md`
- Set status: Pending → In Progress
- Timestamp: start time

### Step 4: Dispatch Codex
```
Use superpowerwithcodex:code-simplification

Technical debt file: docs/specs/<feature>/technical-debt.md
Implementation directory: src/
Tests directory: tests/
```

### Step 5: Automated Verification
After Codex returns:
- Run build command from technical-debt.md
- Run test command (must be 100% green)
- Optional: linting, type checking

### Step 6: Present Merge Options
If verification passes:
```
✅ All verification passed
Choose merge strategy:
A) Auto-merge to main
B) Create PR for review
C) Manual review - show diff
D) Abort - keep worktree
```

### Step 7: Execute Merge & Update Status
- Execute chosen merge strategy
- Update `_technical-debt.md` status: Completed or Failed
- Add summary from progress files

## Key Principles

- **Worktree isolation** - main workspace untouched
- **Automated verification** - build + test must pass
- **User control** - 4 merge options for different risk levels
- **Rollback safety** - failed cleanup can be abandoned
```

### skills/code-simplification/SKILL.md (Codex)

```markdown
---
name: code-simplification
description: Codex native skill for technical debt removal, static analysis, and refactoring - reads technical-debt.md, removes debt items, finds unused code, refactors for simplicity
---

# Code Simplification (Debt Removal + Refactoring)

## Overview

Codex native skill that systematically removes technical debt, performs static analysis to find unused code, and refactors for simplicity. Activates when Claude dispatches with technical-debt.md path.

## When Activated

Claude dispatches via MCP:
```
Use superpowerwithcodex:code-simplification
Technical debt file: docs/specs/<feature>/technical-debt.md
```

## Process

### Entry: Read Technical Debt File
- Parse `technical-debt.md`
- Extract build command, test command
- List all DEBT-N entries

### Phase 1: Debt Removal
For each DEBT-N entry:
1. Remove files/code specified in "What" field
2. Run build command (handles compilation for Java/C++/etc.)
3. Run test command
4. If tests pass:
   - Mark done in `debt-removal-progress.md`
   - Commit: "Remove DEBT-N: <why>"
5. If tests fail:
   - Document issue in `debt-removal-progress.md`
   - Stop and return (Claude will present options)

### Phase 2: Static Analysis
1. Scan for unused code:
   - Unused imports
   - Unused functions (not referenced anywhere)
   - Unused classes (not instantiated)
   - Dead code after returns
2. Write findings to `static-analysis-report.md`
3. Remove safe unused code (not referenced in any file)
4. Run build + test after each removal
5. Commit: "Remove unused code from static analysis"

### Phase 3: Refactoring
Priority order (stop if tests fail at any point):

1. **Extract duplicates:**
   - Find duplicated code blocks (3+ lines, 2+ occurrences)
   - Extract into shared functions
   - Test, commit: "Extract duplicate: <function_name>"

2. **Reduce complexity:**
   - Find functions with cyclomatic complexity > 10
   - Simplify conditionals, extract subfunctions
   - Test, commit: "Reduce complexity in <function_name>"

3. **Apply patterns:**
   - Identify clear pattern opportunities (strategy, factory, etc.)
   - Only apply if obvious value (don't over-engineer)
   - Test, commit: "Apply <pattern> to <component>"

Document each refactoring in `refactor-progress.md` with rationale.

### Return
Write summary:
```
Completed:
- Removed N debt items (X lines deleted)
- Static analysis: Y unused items removed
- Refactored: Z improvements applied

See progress files:
- debt-removal-progress.md
- static-analysis-report.md
- refactor-progress.md
```

## Progress File Formats

### debt-removal-progress.md
```markdown
## Progress
- [x] DEBT-1: Removed old_service.py (tests passed, committed abc123)
- [x] DEBT-2: Removed legacy_auth.py (tests passed, committed def456)
- [ ] DEBT-3: (not started)

## Issues
None
```

### static-analysis-report.md
```markdown
## Unused Imports
- src/utils.py:L3: `import unused_module` (removed)

## Unused Functions
- src/helpers.py:L45-60: `old_helper()` (not referenced, removed)

## Summary
- 3 unused imports removed
- 2 unused functions removed
- 127 lines deleted total
```

### refactor-progress.md
```markdown
## Refactorings Applied

### Extract duplicate: validate_input()
- **Found in:** service.py:L20-25, handler.py:L35-40
- **Extracted to:** utils.py:validate_input()
- **Rationale:** DRY - same validation logic in 2 places
- **Commit:** abc123

### Reduce complexity: process_order()
- **File:** order_service.py:L100-150
- **Before:** Cyclomatic complexity 15
- **After:** Cyclomatic complexity 6
- **Changes:** Extracted subfunctions for validation, payment, fulfillment
- **Commit:** def456
```

## Key Principles

- **Build awareness** - run build command before tests (handles compiled languages)
- **Test after each change** - never accumulate multiple changes before testing
- **Stop on failure** - don't continue if tests fail, return immediately
- **Document everything** - progress files explain all changes
- **Prioritize by impact** - duplicates → complexity → patterns
```

---

## 9. Implementation Plan

### Phase 1: Enhance verify-specs Skill
1. Add Step 4 to `skills/verifying-specs/SKILL.md` (identify technical debt)
2. Implement manual annotation collection (grep for `// DEBT:`)
3. Implement scenario-driven analysis (compare living to REMOVED)
4. Write feature-level technical-debt.md
5. Update project-level _technical-debt.md
6. Add user prompt for cleanup-and-refactor

### Phase 2: Create Codex Native Skill
1. Create `skills/code-simplification/SKILL.md`
2. Implement Phase 1 (debt removal)
3. Implement Phase 2 (static analysis)
4. Implement Phase 3 (refactoring)
5. Test with Codex subagent on sample debt file

### Phase 3: Create Claude Orchestration Skill
1. Create `skills/cleanup-and-refactor/SKILL.md`
2. Implement worktree creation
3. Implement Codex dispatch
4. Implement automated verification
5. Implement merge options presentation
6. Implement status updates to _technical-debt.md

### Phase 4: Integration Testing
1. End-to-end test: verify-specs → cleanup-and-refactor → merge
2. Test with manual annotations (// DEBT: comments)
3. Test with scenario-driven (REMOVED sections)
4. Test with compiled language (Java/C++)
5. Test all merge options (auto-merge, PR, manual, abort)

### Phase 5: Update CLAUDE.md
1. Add cleanup-and-refactor to workflow chain
2. Document technical debt tracking structure
3. Add new skills to Important Files section
4. Update Superpowers Cycle with debt cleanup step

---

## Success Criteria

- [ ] verify-specs identifies both manual and scenario-driven debt
- [ ] technical-debt.md created with structured entries (What, Why, Replaced by, Verification, Source)
- [ ] _technical-debt.md aggregates across all features with status tracking
- [ ] cleanup-and-refactor creates worktree and dispatches Codex
- [ ] code-simplification removes debt, performs static analysis, refactors
- [ ] Automated verification runs build + test before merge
- [ ] Four merge options presented (auto-merge, PR, manual, abort)
- [ ] Status updates flow correctly (Pending → In Progress → Completed/Failed)
- [ ] Works with compiled languages (Java, C++, Go)
- [ ] Rollback safety: failed cleanup can be abandoned without affecting main workspace
- [ ] Progress files document all changes made by Codex
