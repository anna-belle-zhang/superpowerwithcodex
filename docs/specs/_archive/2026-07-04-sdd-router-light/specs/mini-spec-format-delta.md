# Mini-Spec Format Delta Spec

New spec artifact `docs/specs/<feature>/mini.md` and its validation
(`scripts/validate_specs.py`) and directory-convention carve-out
(`tests/structured-specs-integration/`).

## ADDED

### Mini-Spec File Shape
GIVEN a feature routed LIGHT
WHEN its mini-spec is written
THEN docs/specs/<feature>/mini.md contains YAML frontmatter with `mode: light`, a one-sentence intent, a Scenarios section with 2–5 GIVEN/WHEN/THEN scenarios, and an Out of Scope section

### Validator Accepts a Valid Mini-Spec Directory
GIVEN a feature directory containing only a well-formed mini.md
WHEN validate_specs.py runs on that directory
THEN it passes without requiring proposal.md, design.md, or specs/*-delta.md

### Validator Rejects Missing Light Mode
GIVEN a mini.md whose frontmatter lacks `mode: light`
WHEN validate_specs.py runs on the feature directory
THEN it reports an error naming the missing/invalid frontmatter field

### Validator Enforces Scenario Count Bounds
GIVEN a mini.md with fewer than 2 or more than 5 GIVEN/WHEN/THEN scenarios
WHEN validate_specs.py runs on the feature directory
THEN it reports an error stating the scenario count and the allowed range

### Mixing Mini and Delta Specs Is an Error
GIVEN a feature directory containing both mini.md and specs/*-delta.md files
WHEN validate_specs.py runs on that directory
THEN it reports an error stating that a feature must be either LIGHT (mini.md) or FULL (proposal/design/deltas), not both

### Directory Convention Carve-Out
GIVEN the structured-specs-integration convention tests
WHEN they check feature directory structure
THEN a feature directory containing mini.md is allowed to omit proposal.md, design.md, and the specs/ subdirectory, while FULL feature directories keep the existing requirements

## MODIFIED

### Full-Directory Validation Unchanged for FULL Features
**Was:** validate_specs.py validates every feature directory against the FULL layout (proposal.md, design.md, specs/*-delta.md)
**Now:** the FULL layout is required only when mini.md is absent
**Reason:** LIGHT features carry their whole contract in mini.md

GIVEN a feature directory without mini.md
WHEN validate_specs.py runs on that directory
THEN the existing FULL-layout validation applies exactly as before
