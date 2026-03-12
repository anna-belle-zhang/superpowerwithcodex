# Code Simplification — Baseline Behavior (No Skill)

## Scenario Tested

Codex is dispatched with a feature debt file and asked to clean up technical debt autonomously.

## Expected Risk Without Skill

- `technical-debt.md` may be read loosely instead of as a contract
- Debt items may be batched together instead of removed one at a time
- Build/test order may be inconsistent after edits
- Static analysis may scan the full repo instead of feature-touched files only
- Refactoring failures may leave broken code in place instead of reverting and continuing
- Progress files and commit-message conventions may be omitted

## Conclusion

The skill must force three explicit phases:
`debt removal → scoped static analysis → targeted refactoring`
