# Mini-Spec Format - Living Spec

The `docs/specs/<feature>/mini.md` artifact, its validation
(`scripts/validate_specs.py`), and the directory-convention carve-out
(`tests/structured-specs-integration/`).

## Behaviors

### Mini-Spec File Shape
GIVEN a feature routed LIGHT
WHEN its mini-spec is written
THEN docs/specs/<feature>/mini.md contains YAML frontmatter with `mode: light`, a one-sentence intent, a Scenarios section with 2–5 GIVEN/WHEN/THEN scenarios, and an Out of Scope section

*Added: 2026-07-04 via sdd-router-light*

### Validator Accepts a Valid Mini-Spec Directory
GIVEN a feature directory containing only a well-formed mini.md
WHEN validate_specs.py runs on that directory
THEN it passes without requiring proposal.md, design.md, or specs/*-delta.md

*Added: 2026-07-04 via sdd-router-light*

### Validator Rejects Missing Light Mode
GIVEN a mini.md whose frontmatter lacks `mode: light`
WHEN validate_specs.py runs on the feature directory
THEN it reports an error naming the missing/invalid frontmatter field

*Added: 2026-07-04 via sdd-router-light*

### Validator Enforces Scenario Count Bounds
GIVEN a mini.md with fewer than 2 or more than 5 GIVEN/WHEN/THEN scenarios
WHEN validate_specs.py runs on the feature directory
THEN it reports an error stating the scenario count and the allowed range

*Added: 2026-07-04 via sdd-router-light*

### Mixing Mini and Delta Specs Is an Error
GIVEN a feature directory containing both mini.md and specs/*-delta.md files
WHEN validate_specs.py runs on that directory
THEN it reports an error stating that a feature must be either LIGHT (mini.md) or FULL (proposal/design/deltas), not both

*Added: 2026-07-04 via sdd-router-light*

### Directory Convention Carve-Out
GIVEN the structured-specs-integration convention tests
WHEN they check feature directory structure
THEN a feature directory containing mini.md is allowed to omit proposal.md, design.md, and the specs/ subdirectory, while FULL feature directories keep the existing requirements

*Added: 2026-07-04 via sdd-router-light*

### Full-Directory Validation Unchanged for FULL Features
GIVEN a feature directory without mini.md
WHEN validate_specs.py runs on that directory
THEN the existing FULL-layout validation applies exactly as before

*Modified: 2026-07-04 via sdd-router-light (was: validate_specs.py validated every feature directory against the FULL layout unconditionally)*
