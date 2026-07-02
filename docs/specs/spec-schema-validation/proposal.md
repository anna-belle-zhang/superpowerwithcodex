# Spec Schema Validation Proposal

## Intent

Delta specs are the contract between Claude (spec author) and Codex (implementer). Today the only guard against malformed specs is the LLM three-check in verifying-specs, which runs after implementation — a spec missing its GIVEN/WHEN/THEN lines is discovered only after Codex has already burned a dispatch cycle on an ambiguous contract. A deterministic validator catches structural defects before dispatch, when they cost seconds instead of a full Codex round-trip.

## Scope

**In scope:**
- `scripts/validate_specs.py` — a zero-dependency Python script that validates one feature spec directory (`docs/specs/<feature>/`) against the repo's structured-spec conventions and exits non-zero on any violation
- Machine-checkable rules only: file presence, required sections, GIVEN/WHEN/THEN completeness, MODIFIED/REMOVED field requirements, cross-section conflicts

**Out of scope:**
- Semantic checks (scenario quality, contradiction with living specs) — those remain in verifying-specs' LLM checks
- Wiring the validator into write-specs / claude-codex-specs-tdd / verify-specs skill documents (done separately as skill edits by Claude)
- Validating `_living/`, `_archive/`, or `_technical-debt.md`
- A watch mode or CI integration

## Impact

- **Users affected:** anyone running the specs-first workflow in this repo
- **Systems affected:** new `scripts/` directory; new tests under `tests/`; three skill documents gain a validation step (separate change)
- **Risk:** low — read-only script, no changes to existing code paths

## Success Criteria

- [ ] `python scripts/validate_specs.py docs/specs/<feature>/` exits 0 on a well-formed feature directory and 1 on any violation
- [ ] Every violation is reported as one line naming the file and the problem
- [ ] All existing committed feature spec directories under `docs/specs/` (excluding `_living`, `_archive`) can be checked; findings against them are reported, not crashed on
- [ ] Full pytest suite passes
