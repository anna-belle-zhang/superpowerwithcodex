# Technical Debt Cleanup & Refactoring Design

## Architecture

Two-tier skill architecture following the Claude-Codex pattern:

**Claude orchestration layer:**
- `cleanup-and-refactor` skill coordinates workflow
- Creates isolated worktree for safety
- Dispatches Codex with technical debt file path
- Runs automated verification (build + test)
- Presents merge options based on verification results

**Codex execution layer:**
- `code-simplification` skill performs actual code changes
- Three-phase process: debt removal → static analysis → refactoring
- Writes three separate progress files for transparency
- Stops immediately on test failure

**Integration point:**
- `verify-specs` enhanced with Step 4 for debt identification
- Two-phase identification: manual annotations + scenario-driven analysis
- Creates feature-level debt file, updates project-level tracker

## Components

### verify-specs Enhancement
**Responsibility:** Identify technical debt after scenario verification

**Inputs:**
- Codebase source files (scan for `// DEBT:` comments)
- `docs/specs/_living/*.md` (current system behaviors)
- Delta specs with REMOVED sections

**Outputs:**
- `docs/specs/<feature>/technical-debt.md` (structured entries)
- `docs/specs/_technical-debt.md` (project-level aggregation)
- User prompt: "Run cleanup-and-refactor now?"

### cleanup-and-refactor (Claude)
**Responsibility:** Orchestrate safe debt removal workflow

**Inputs:**
- Feature name
- `docs/specs/<feature>/technical-debt.md`

**Outputs:**
- Isolated worktree on `cleanup/<feature>` branch
- Codex dispatch with debt file path
- Verification results (build + test)
- Merge execution (based on user choice)
- Updated `_technical-debt.md` with status changes

### code-simplification (Codex)
**Responsibility:** Execute debt removal, static analysis, refactoring

**Inputs:**
- `technical-debt.md` (debt items + build/test commands)

**Outputs:**
- Modified codebase (debt removed, refactored)
- `debt-removal-progress.md` (checklist with commits)
- `static-analysis-report.md` (unused code findings)
- `refactor-progress.md` (refactorings applied with rationale)

## Data Flow

```
Implementation Phase:
  Developer writes code
  → Adds // DEBT: comments when noticing old code

Verification Phase:
  verify-specs runs
  → Step 1-3: Check scenarios (completeness/correctness/coherence)
  → Step 4a: Grep for // DEBT: comments
  → Step 4b: Compare _living/ specs to REMOVED in delta specs
  → Step 4c: Write technical-debt.md (feature-level)
  → Step 4d: Update _technical-debt.md (project-level, status: Pending)
  → Step 4e: Prompt user "Run cleanup-and-refactor?"

Cleanup Phase (if user says yes):
  cleanup-and-refactor (Claude):
    → Create worktree on cleanup/<feature>
    → Update _technical-debt.md (status: In Progress)
    → Dispatch Codex with debt file path

  code-simplification (Codex):
    → Read technical-debt.md
    → Phase 1: Remove each debt item, test after each
    → Phase 2: Static analysis, remove unused code
    → Phase 3: Refactor (duplicates → complexity → patterns)
    → Write progress files
    → Return

  cleanup-and-refactor (Claude):
    ← Read progress files
    → Run build command
    → Run test command
    → If pass: present merge options
    → If fail: show errors, offer retry/abort
    → Execute user's merge choice
    → Update _technical-debt.md (status: Completed/Failed)
```

## Error Handling

### Debt Identification Failures
- **No design doc found:** Prompt to run brainstorming first
- **No REMOVED sections and no // DEBT: comments:** Skip Step 4, continue to archive-specs
- **Living spec file missing:** Warning only, continue (feature may not modify existing behavior)

### Cleanup Execution Failures
- **Worktree creation fails:** Check for existing worktree, offer to delete and retry
- **Build fails after debt removal:** Stop immediately, document in progress file, return to Claude
- **Tests fail after debt removal:** Stop immediately, document failure, return to Claude
- **Codex dispatch timeout:** Retry once, then abort and keep worktree for manual inspection

### Verification Failures
- **Build fails:** Show build output, offer: retry | manual fix | abort
- **Tests fail:** Show test output, offer: retry | manual fix | abort
- **Static checks fail (if enabled):** Warning only, don't block merge

### Merge Failures
- **Auto-merge conflicts:** Fall back to PR creation
- **PR creation fails (no gh CLI):** Show manual git commands
- **Main branch dirty:** Error, require clean state before merge

## Dependencies

### External Tools
- **Git:** Required for worktree creation, branch management, merge
- **GitHub CLI (optional):** For PR creation merge option
- **Build tools:** Language-specific (Maven, Gradle, CMake, npm, etc.)
- **Test runners:** Language-specific (JUnit, pytest, Jest, etc.)

### Internal Skills
- `superpowerwithcodex:using-git-worktrees` - Worktree creation pattern
- `superpowerwithcodex:verifying-specs` - Enhanced with debt identification
- `superpowerwithcodex:archiving-specs` - Called after cleanup completes

### MCP Integration
- `codex-as-mcp` server - Dispatch mechanism for Codex subagent
- Codex receives `superpowerwithcodex:code-simplification` activation prompt

## Technical Decisions

### Why Two-Phase Debt Identification?
- **Manual annotations:** Developers notice debt during implementation, marking it explicitly
- **Scenario-driven:** Systematic check catches debt that developers missed
- **Combination:** Comprehensive coverage without relying on perfect human discipline

### Why Separate Progress Files?
- **Transparency:** Each phase (removal, static analysis, refactoring) documented separately
- **Debugging:** Easy to identify which phase failed
- **Review:** User can see exactly what Codex changed and why

### Why Worktree Isolation?
- **Safety:** Main workspace untouched during risky cleanup operations
- **Rollback:** Failed cleanup simply deletes worktree, no git reset needed
- **Parallel work:** User can continue in main workspace while cleanup runs

### Why Four Merge Options?
- **Auto-merge:** Fast path for solo developers with clean repos
- **PR:** Standard for teams with code review requirements
- **Manual review:** Safety for high-risk cleanup operations
- **Abort:** Investigation path when results are unexpected

### Why Prioritized Refactoring?
- **Duplicates first:** Highest ROI (immediate reduction in maintenance burden)
- **Complexity second:** Improves readability and testability
- **Patterns last:** Only when clear value (avoid over-engineering)
- **Stop on failure:** Don't accumulate multiple risky changes before testing
