# SDD Router - Living Spec

Entry routing by risk and complexity (`skills/sdd-router/`).

## Behaviors

### Risk Hit Forces FULL
GIVEN a request that affects production systems, writes or deletes data, changes an API signature, or touches privacy/compliance/core data
WHEN the router classifies the request
THEN it recommends FULL with a one-line reason naming the risk hit, regardless of how simple the change is

*Added: 2026-07-04 via sdd-router-light*

### Low Complexity Routes LIGHT
GIVEN a request that hits no risk check and is a config change, bugfix, or single-file change
WHEN the router classifies the request
THEN it recommends LIGHT with a one-line reason

*Added: 2026-07-04 via sdd-router-light*

### High Complexity Routes FULL
GIVEN a request that hits no risk check but involves a new module, multiple files, or crosses frontend/backend boundaries
WHEN the router classifies the request
THEN it recommends FULL with a one-line reason

*Added: 2026-07-04 via sdd-router-light*

### Uncertainty Escalates
GIVEN a request whose risk or complexity classification is ambiguous
WHEN the router classifies the request
THEN it escalates one level (a doubtful LIGHT becomes FULL) and says so in the reason

*Added: 2026-07-04 via sdd-router-light*

### User Confirms or Overrides the Tier
GIVEN the router has produced a recommendation and reason
WHEN it presents the recommendation
THEN it waits for the user to confirm or override before any spec or code work starts, and the user's choice is final

*Added: 2026-07-04 via sdd-router-light*

### Override Does Not Silence Risk
GIVEN the router found a risk hit and recommended FULL
WHEN the user overrides to LIGHT
THEN the router proceeds LIGHT but the risk hit and its reason remain stated in the conversation and recorded in the mini-spec's out-of-scope/notes

*Added: 2026-07-04 via sdd-router-light*

### Context Restore Before Classification
GIVEN docs/handovers/LATEST.md exists
WHEN the router starts on a new request
THEN it reads the handover it points to before classifying, so restored decisions inform the tier

*Added: 2026-07-04 via sdd-router-light*

### No Handover, No Fabrication
GIVEN docs/handovers/LATEST.md does not exist
WHEN the router starts on a new request
THEN it proceeds with classification without fabricating prior context

*Added: 2026-07-04 via sdd-router-light*

### LIGHT Route Produces a Mini-Spec Then Dispatches
GIVEN the user confirmed LIGHT
WHEN the router executes the LIGHT route
THEN it writes docs/specs/<feature>/mini.md, gets user approval of the scenarios, and dispatches Codex using the standard dispatch format with the spec directory path

*Added: 2026-07-04 via sdd-router-light*

### FULL Route Delegates Unchanged
GIVEN the user confirmed FULL
WHEN the router executes the FULL route
THEN it hands off to the existing brainstorming → write-specs → spec-driven-tdd chain without duplicating any of their steps

*Added: 2026-07-04 via sdd-router-light*

### No Zero-Spec Channel
GIVEN the user says the change is urgent and asks to skip specs entirely
WHEN the router handles the request
THEN it still produces a mini.md before any implementation code — LIGHT is the minimum process weight, and no route skips scenarios

*Added: 2026-07-04 via sdd-router-light*
