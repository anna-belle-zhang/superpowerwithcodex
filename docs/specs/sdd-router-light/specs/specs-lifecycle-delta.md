# Specs Lifecycle Delta Spec

`skills/verifying-specs/SKILL.md` and `skills/archiving-specs/SKILL.md` —
LIGHT features flow through verify and archive with no second-class treatment.

## MODIFIED

### Verify Reads Scenarios From Mini-Specs Too
**Was:** verify-specs reads scenarios only from `docs/specs/<feature>/specs/*-delta.md`
**Now:** when the feature directory contains mini.md, verify-specs reads its scenarios instead
**Reason:** the completeness/correctness/coherence checks are about scenarios, not about which file carries them

GIVEN a LIGHT feature directory with mini.md and an implementation with tests
WHEN verify-specs runs
THEN it produces the same scenario→test coverage table (COVERED/MISSING per scenario) sourced from mini.md scenarios

### Archive Merges Mini-Spec Scenarios Into Living Specs
**Was:** archive-specs merges only `<component>-delta.md` files into `docs/specs/_living/<component>.md`
**Now:** for LIGHT features, mini.md scenarios are merged into the appropriate `_living/<component>.md` as added behaviors with the standard attribution line, and the feature directory is archived to `_archive/YYYY-MM-DD-<feature>/` the same as FULL features
**Reason:** living specs must stay the single source of truth; a behavior shipped via LIGHT is no less real

GIVEN a verified LIGHT feature with mini.md
WHEN archive-specs runs
THEN each mini.md scenario appears in `docs/specs/_living/` with an "Added: YYYY-MM-DD via <feature>" attribution and the feature directory moves to `docs/specs/_archive/YYYY-MM-DD-<feature>/`

### Coherence Check Includes Mini-Specs
**Was:** the coherence check compares delta specs against each other and `_living/`
**Now:** mini.md scenarios participate in the same contradiction check against `_living/`
**Reason:** a LIGHT scenario can contradict existing system behavior just as a delta can

GIVEN a mini.md scenario that contradicts a behavior in `docs/specs/_living/`
WHEN verify-specs runs its coherence check
THEN the contradiction is reported as a failure, the same as it would be for a delta spec
