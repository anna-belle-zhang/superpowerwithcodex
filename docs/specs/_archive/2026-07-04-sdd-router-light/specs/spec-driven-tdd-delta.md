# spec-driven-tdd Delta Spec

`skills/spec-driven-tdd/SKILL.md` — the spec fingerprint supports mini-spec
features. The TDD loop, progress.md format, and re-entry discipline are
otherwise unchanged.

## MODIFIED

### Fingerprint File Set Depends on Spec Mode
**Was:** the spec fingerprint is always `sha256sum proposal.md design.md specs/*-delta.md`
**Now:** when `mini.md` exists in the feature directory, the fingerprint is the sha256 of `mini.md` alone; otherwise the FULL file set applies as before
**Reason:** LIGHT features have no proposal/design/deltas; the fingerprint must cover exactly the files the plan was derived from

GIVEN a feature directory containing mini.md
WHEN Codex records the spec fingerprint in progress.md
THEN the fingerprint covers mini.md alone

GIVEN a feature directory without mini.md
WHEN Codex records the spec fingerprint in progress.md
THEN the fingerprint covers proposal.md, design.md, and specs/*-delta.md exactly as before

### Re-Entry Verifies the Mode-Appropriate Fingerprint
**Was:** re-entry recomputes the FULL file set and compares against progress.md
**Now:** re-entry recomputes whichever file set the mode implies (mini.md alone for LIGHT) before trusting any [x] task
**Reason:** a stale mini.md invalidates completed tasks the same way a stale delta does

GIVEN a LIGHT feature with progress.md whose recorded fingerprint no longer matches the current mini.md hash
WHEN Codex re-enters the feature
THEN it treats affected [x] tasks as reopened, exactly as the existing stale-fingerprint rule requires

## ADDED

### Mini-Spec Scenarios Are the Same Contract
GIVEN Codex is dispatched with a spec directory containing mini.md
WHEN it derives its plan and unit tests
THEN every mini.md scenario maps to at least one test and no scenario is treated as optional because the spec is "light"
