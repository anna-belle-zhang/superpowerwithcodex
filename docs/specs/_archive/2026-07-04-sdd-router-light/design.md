# sdd-router + LIGHT Channel Design

Source: `docs/plans/2026-07-03-flow-layer-design.md` (approved brainstorm),
sdd-router section. Core principle: **orchestrate, don't rebuild** — the router
routes into existing workflows; it does not duplicate brainstorming,
writing-specs, or spec-driven-tdd.

## Architecture

```
skills/sdd-router/SKILL.md      # NEW: entry routing (risk + complexity → FULL/LIGHT)
hooks/prompt-submit.sh          # MODIFIED: tiered rules replace "always FULL"
skills/spec-driven-tdd/SKILL.md # MODIFIED: fingerprint supports mini.md
scripts/validate_specs.py       # MODIFIED: validates mini-spec feature dirs
tests/structured-specs-integration/  # MODIFIED: convention carve-out + new tests
skills/verifying-specs/SKILL.md # MODIFIED: read scenarios from mini.md too
skills/archiving-specs/SKILL.md # MODIFIED: merge mini.md scenarios into _living/
```

## Components

### sdd-router (new skill)

Runs at the start of feature work. Steps:

1. **Context restore** — read `docs/handovers/LATEST.md` if present (handover-manager
   living spec governs fallback behavior; router just reads).
2. **Classify** — risk checks first, then complexity:

```yaml
risk_checks:        # any hit → FULL, regardless of complexity
  - affects real users or production systems
  - writes/deletes data, or changes an API signature
  - touches privacy, compliance, or core data
complexity:
  high: new module, multi-file, cross frontend/backend  → FULL
  low:  config change, bugfix, single file              → LIGHT
uncertain: escalate one level (doubtful LIGHT → FULL)
```

3. **Recommend** — output tier + one-line reason; wait for user confirmation or
   one-word override. Tiering authority always stays with the human.
4. **Route** — FULL: existing brainstorm → write-specs → spec-driven-tdd chain,
   unchanged. LIGHT: write `mini.md`, then dispatch Codex with the standard
   dispatch format (same as FULL — spec directory path only).

### Mini-spec format

`docs/specs/<feature>/mini.md`:

```markdown
---
mode: light
feature: <feature-name>
date: YYYY-MM-DD
---

# <Feature> — Mini Spec

Intent: <one sentence>

## Scenarios

### <Behavior Name>
GIVEN ... WHEN ... THEN ...

(2–5 scenarios total)

## Out of Scope
- <exclusion 1>
```

A feature directory is either LIGHT (`mini.md`, no proposal/design/deltas
required) or FULL (proposal/design/deltas, no mini.md) — never both. Mixing
makes the spec fingerprint ambiguous and is a validation error.

## Data Flow

new request → sdd-router (reads LATEST.md, classifies, user confirms)
→ LIGHT: mini.md → Codex (spec-driven-tdd, fingerprint = sha256 of mini.md alone)
→ FULL: unchanged existing chain
→ both: verify-specs (scenario→test coverage) → archive-specs (merge into _living/)

## Error Handling

- Missing/broken `LATEST.md`: handover-manager living-spec behaviors apply
  (fallback to newest handover, or proceed without fabricating state).
- Uncertain classification: escalate to FULL — never silently downgrade.
- User pressure to skip specs ("urgent, just do it"): LIGHT is the floor;
  mini.md is still written. Risk hits are always reported even if the user
  overrides the tier.
- `mini.md` + delta specs in the same feature dir: validate_specs.py reports
  an error.

## Dependencies

- handover-manager (`docs/specs/_living/handover-manager.md`) — LATEST.md
  read behavior; shipped.
- Existing skills reused unchanged in behavior: brainstorming, writing-specs
  (FULL path), spec-driven-tdd TDD loop (only the fingerprint file set changes).

## Testing Strategy

- **Deterministic (pytest, `tests/structured-specs-integration/`):** mini.md
  frontmatter validation, scenario count bounds, directory-convention carve-out,
  mixing error, hook rule text mentions both tiers.
- **Skill pressure tests (writing-skills iron law):** baseline without skill,
  then with. Key scenario: "urgent, just change it" — router must still
  produce a mini.md and report risk hits.
