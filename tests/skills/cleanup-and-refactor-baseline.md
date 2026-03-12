# Cleanup And Refactor — Baseline Behavior (No Skill)

## Scenario Tested

User asks to clean up tracked technical debt for a feature that already has `docs/specs/<feature>/technical-debt.md`.

## Expected Risk Without Skill

- Validation is inconsistent: the agent may skip checking for `technical-debt.md`
- Base branch cleanliness is easy to miss before creating a worktree
- Worktree naming and reuse behavior are not standardized
- Codex dispatch prompt may omit the exact `code-simplification` activation text
- Verification ordering may drift to tests-before-build instead of build-before-tests
- Merge options and debt-status updates are easy to under-specify

## Conclusion

The skill needs to force a repeatable orchestration sequence:
`validate → worktree → status update → Codex dispatch → build/test verification → merge choice → status finalization`
