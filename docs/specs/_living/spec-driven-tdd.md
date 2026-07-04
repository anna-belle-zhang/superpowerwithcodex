# Spec-Driven TDD - Living Spec

`skills/spec-driven-tdd/SKILL.md` — Codex-side implementation workflow.

## Behaviors

### Fingerprint File Set Depends on Spec Mode
GIVEN a feature directory containing mini.md
WHEN Codex records the spec fingerprint in progress.md
THEN the fingerprint covers mini.md alone

GIVEN a feature directory without mini.md
WHEN Codex records the spec fingerprint in progress.md
THEN the fingerprint covers proposal.md, design.md, and specs/*-delta.md exactly as before

*Modified: 2026-07-04 via sdd-router-light (was: fingerprint was always sha256 of proposal.md + design.md + specs/*-delta.md)*

### Re-Entry Verifies the Mode-Appropriate Fingerprint
GIVEN a LIGHT feature with progress.md whose recorded fingerprint no longer matches the current mini.md hash
WHEN Codex re-enters the feature
THEN it treats affected [x] tasks as reopened, exactly as the existing stale-fingerprint rule requires

*Modified: 2026-07-04 via sdd-router-light (was: re-entry recomputed only the FULL file set)*

### Mini-Spec Scenarios Are the Same Contract
GIVEN Codex is dispatched with a spec directory containing mini.md
WHEN it derives its plan and unit tests
THEN every mini.md scenario maps to at least one test and no scenario is treated as optional because the spec is "light"

*Added: 2026-07-04 via sdd-router-light*
