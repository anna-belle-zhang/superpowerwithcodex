# Specs Workflow Skill Gaps Fix Proposal

## Intent

The 2026-06-13 review of nine OpenMetadata features produced by this plugin's specs workflow (`docs/2026-06-13-specs-process-review-analysis.md`) found that every recurring defect traces to three structural gaps in the workflow skills — gaps that persist with a healthy model because the instructions never existed:

1. **Stale system index** (finding #1): no skill maintains `_living/ARCHITECTURE.md`, so it drifted 6 weeks and 11 specs behind.
2. **Dead debt pipeline** (finding #2): no upstream skill tells Codex to write `DEBT:` annotations; the `verifying-specs` scan hardcodes C-style `// DEBT:` and never matches Python/SQL; debt recorded in `progress.md` Issues is never read.
3. **Blind archive move** (findings #3, #5, #6): `archiving-specs` moves the feature directory without checking completeness, letting missing progress.md, stray specs, and junk files into the archive.

Additionally, the debt section of `verifying-specs` was authored during the March 2026 regression window (commit `91da369`) and contains a duplicated contradictory branch (finding #7).

This feature closes all four by editing three skill files.

## Scope

**In scope:**
- `skills/verifying-specs/SKILL.md` — branch dedup, language-aware DEBT scan, progress.md Issues as a debt source, full proofread
- `skills/spec-driven-tdd/SKILL.md` — instruct Codex to annotate compromises at creation time
- `skills/archiving-specs/SKILL.md` — system-index maintenance step, pre-archive completeness check, proofread
- Consistent skill cross-reference namespacing in the edited files

**Out of scope:**
- OpenMetadata repo cleanup (companion plan `2026-06-13-specs-hardening-and-upstream-alignment.md` — executed after this feature so the new steps are exercised on the backfill)
- Hook changes (`hooks/hooks.json`)
- Any production code; this feature is process-doc edits only

## Impact

- **Users affected:** anyone running the specs workflow (verify-specs / archive-specs commands; Codex dispatched via spec-driven-tdd)
- **Systems affected:** three skill files; behavior of future verification and archiving runs
- **Risk:** low — markdown edits to process docs, each independently verifiable by grep/pytest; no runtime code touched

## Success Criteria

- [ ] Every scenario in the three delta specs has a corresponding passing test
- [ ] No `// DEBT:`-only hardcoding remains anywhere in `skills/`
- [ ] `archiving-specs` overview lists six steps including the index update
- [ ] Subagent dry-run on a toy feature produces `technical-debt.md` and updates a stub ARCHITECTURE.md
- [ ] Conventions suite (`pytest tests/structured-specs-integration/`) passes
