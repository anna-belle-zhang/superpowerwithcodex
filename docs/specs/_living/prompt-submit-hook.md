# Prompt-Submit Hook - Living Spec

`hooks/prompt-submit.sh` — mandatory workflow rules injected every turn.

## Behaviors

### Specs-Before-Code Rule Is Tiered
GIVEN the prompt-submit hook fires
WHEN its injected rules are read
THEN rule 1 states that spec weight is tiered by the sdd-router (FULL = proposal/design/deltas, LIGHT = mini.md), that any risk hit forces FULL, and that no code is written without one of the two

*Modified: 2026-07-04 via sdd-router-light (was: rule 1 mandated the FULL workflow for every request)*

### Injected Rules Name the Router as Entry Point
GIVEN the prompt-submit hook fires
WHEN its injected rules are read
THEN they instruct starting feature work with the sdd-router skill and still list the existing brainstorm/write-specs/verify-specs/archive-specs commands for the FULL path

*Modified: 2026-07-04 via sdd-router-light (was: rule 4 listed brainstorm as the first command before any feature work)*

### Dispatch Format and Remaining Rules Unchanged
GIVEN the prompt-submit hook fires
WHEN its injected rules are read
THEN the dispatch format, the no-unit-tests-by-Claude rule, and the verification-before-done rule are present and unchanged in meaning — LIGHT features use the same dispatch format with their spec directory

*Modified: 2026-07-04 via sdd-router-light (was: same rules, restated to confirm the LIGHT channel does not alter them)*
