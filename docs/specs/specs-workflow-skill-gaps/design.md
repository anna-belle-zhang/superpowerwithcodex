# Specs Workflow Skill Gaps Fix Design

## Architecture

All changes are edits to skill markdown in `skills/`. No production code. The "implementation" is process-doc content; verification is grep/pytest assertions against the edited files plus one subagent dry-run per `testing-skills-with-subagents`.

The debt pipeline becomes a connected chain with three sources feeding one sink:

```
spec-driven-tdd (Codex, creation time)
  compromise → DEBT: comment (native syntax) + progress.md ## Issues entry
        │
        ▼
verifying-specs Step 4 (Claude, verification time)
  4a: language-aware DEBT: scan  ──┐
  4b: REMOVED-delta analysis      ─┼─→ technical-debt.md + _technical-debt.md
  4b-2: progress.md Issues scan  ──┘
        │
        ▼
archiving-specs (Claude, archive time)
  2.5: update _living/ARCHITECTURE.md index
  2.6: pre-archive completeness check
  3:   move to _archive (no longer blind)
```

## Components

- **`skills/verifying-specs/SKILL.md`** — Step 4e branch dedup (regression artifact, commit `91da369`); Step 4a scan generalized to `(#|//|--|<!--) ?DEBT:`; new Step 4b-2 reads `## Issues` from progress.md; skip condition and summary template extended.
- **`skills/spec-driven-tdd/SKILL.md`** — TDD loop gains a step: any compromise gets a `DEBT:` comment at the code site in the file's native comment syntax AND an `## Issues` entry; Red Flags list gains the inverse.
- **`skills/archiving-specs/SKILL.md`** — new Step 2.5 (system index): every living spec reachable from ARCHITECTURE.md, "as of" date refreshed, skip when no index exists; new Step 2.6 (completeness check): progress.md required (STOP if missing), strays relocated to `specs/`, junk deleted; overview renumbered to six steps.

## Data Flow

Debt facts flow from creation site (code comments, progress.md Issues) through verification (collected into `docs/specs/<feature>/technical-debt.md` and the project ledger `docs/specs/_technical-debt.md`) to the cleanup-and-refactor offer. Index facts flow from Step 2's living-spec writes into ARCHITECTURE.md entries.

## Error Handling

- Missing progress.md at verification: Step 4b-2 continues without failure (not alone a failure).
- Missing progress.md at archiving: Step 2.6 STOPs and asks (backfill stub vs. proceed with noted gap).
- Missing ARCHITECTURE.md: Step 2.5 skipped; optionally offer creation once ≥ 3 living specs exist.
- Missing proposal.md/design.md at archiving: warn, don't block.
- Narrative-only Issues entries: judged not-debt (future work implied = debt; narration = not).

## Dependencies

- `docs/specs/_living/verifying-specs.md` — existing living spec; changed behaviors are MODIFIED deltas against it.
- Companion OpenMetadata plan executes after this feature to exercise the new steps on real backfill.
- Plan: `docs/plans/2026-06-13-specs-workflow-skill-gaps-fix.md` (Tasks 1–7). Note: Task 7's premise is corrected by the analysis — only `verifying-specs`' debt section was window-authored; `archiving-specs` (2026-02-19) is proofread on its own merits.
