# Prompt-Submit Hook Delta Spec

`hooks/prompt-submit.sh` — the rules injected every turn become router-aware.

## MODIFIED

### Specs-Before-Code Rule Is Tiered
**Was:** rule 1 mandates the FULL workflow for every request ("Never write implementation code without specs... Brainstorm first → write specs → dispatch Codex")
**Now:** rule 1 keeps specs-before-code but tiers the weight by router decision: FULL = proposal/design/deltas, LIGHT = mini.md; any risk hit forces FULL
**Reason:** config tweaks and one-line bugfixes should not pay the full spec cost, but must never ship without scenarios

GIVEN the prompt-submit hook fires
WHEN its injected rules are read
THEN rule 1 states that spec weight is tiered by the sdd-router (FULL = proposal/design/deltas, LIGHT = mini.md), that any risk hit forces FULL, and that no code is written without one of the two

### Injected Rules Name the Router as Entry Point
**Was:** rule 4 lists brainstorm as the first command before any feature work
**Now:** the rules direct feature work through sdd-router first, which routes to brainstorm (FULL) or mini-spec (LIGHT)
**Reason:** the router is the new entry; brainstorming remains the FULL path's first step

GIVEN the prompt-submit hook fires
WHEN its injected rules are read
THEN they instruct starting feature work with the sdd-router skill and still list the existing brainstorm/write-specs/verify-specs/archive-specs commands for the FULL path

### Dispatch Format and Remaining Rules Unchanged
**Was:** rules 2 (dispatch format), 3 (Claude never writes unit/integration tests), and 5 (verification before claiming done) as currently injected
**Now:** identical — LIGHT features use the same dispatch format with their spec directory
**Reason:** the LIGHT channel changes spec weight, not the Codex contract or verification discipline

GIVEN the prompt-submit hook fires after this change
WHEN its injected rules are read
THEN the dispatch format, the no-unit-tests-by-Claude rule, and the verification-before-done rule are present and unchanged in meaning
