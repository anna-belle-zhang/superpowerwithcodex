# Technical Debt Cleanup & Refactoring Proposal

## Intent

Technical debt accumulates during feature development when old code gets replaced but not systematically removed. This creates maintenance burden, increases cognitive load for developers, and introduces potential bugs from outdated code paths. This feature integrates technical debt tracking and systematic cleanup into the spec-driven workflow, ensuring debt is identified, tracked, and removed safely.

## Scope

**In scope:**
- Two-phase debt identification (manual `// DEBT:` annotations + scenario-driven analysis)
- Feature-level and project-level debt tracking files
- New Claude skill: `cleanup-and-refactor` (orchestration via worktree)
- New Codex skill: `code-simplification` (execution: debt removal + static analysis + refactoring)
- Integration with `verify-specs` skill for automatic debt identification
- Automated verification (build + test) before merge
- Four merge strategies (auto-merge, PR, manual review, abort)

**Out of scope:**
- Automated debt prioritization (users manually set priority in tracking file)
- Cross-repository debt tracking (project-level only)
- Automatic scheduling of debt cleanup (user decides when to run)
- Integration with issue tracking systems (Jira, GitHub Issues)

## Impact

- **Users affected:** All superpowerwithcodex users following spec-driven workflow
- **Systems affected:**
  - `skills/verifying-specs/` (enhanced with Step 4: debt identification)
  - `skills/cleanup-and-refactor/` (new Claude skill)
  - `skills/code-simplification/` (new Codex skill)
  - `docs/specs/_technical-debt.md` (new project-level tracker)
  - `docs/specs/<feature>/technical-debt.md` (new feature-level files)
- **Risk:** Medium
  - Worktree isolation provides safety for cleanup operations
  - Automated verification gates merge to prevent broken code
  - Rollback capability if cleanup fails
  - Main risk: false positives in static analysis (mitigated by testing after each removal)

## Success Criteria

- [ ] `verify-specs` identifies debt from both manual annotations and scenario-driven analysis
- [ ] Feature-level `technical-debt.md` created with structured entries (What, Why, Replaced by, Verification, Source)
- [ ] Project-level `_technical-debt.md` aggregates across features with status tracking (Pending → In Progress → Completed/Failed)
- [ ] `cleanup-and-refactor` creates isolated worktree and dispatches Codex successfully
- [ ] `code-simplification` removes debt, performs static analysis, and refactors code
- [ ] Automated verification (build + test) runs before merge and blocks on failure
- [ ] All four merge options work correctly (auto-merge, PR, manual review, abort)
- [ ] Works with compiled languages (Java, C++, Go) via build command execution
- [ ] Progress files document all changes made by Codex
- [ ] End-to-end test: verify-specs → cleanup-and-refactor → merge completes successfully
