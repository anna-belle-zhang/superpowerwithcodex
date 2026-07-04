---
name: sdd-router
description: Use when starting feature work to route a request to FULL specs or LIGHT mini-specs by risk, complexity, and user confirmation
---

# SDD Router

Route feature work into the right spec weight before any code is written.

**Core principle:** LIGHT is the minimum process weight, not a shortcut around scenarios. FULL remains the path for risk, complexity, and uncertainty.

**Announce at start:** "I'm using the sdd-router skill to choose FULL or LIGHT spec workflow."

## The Process

### Step 1: Restore Context

If `docs/handovers/LATEST.md` exists, read it before classifying the new request. Use restored decisions and open items as context for the tier recommendation.

If `docs/handovers/LATEST.md` does not exist, proceed with classification without fabricating prior context.

### Step 2: Classify Risk First

Any risk hit forces `FULL`, regardless of how small the implementation looks. Name the risk hit in a one-line reason.

Risk hits:
- Affects real users or production systems
- Writes or deletes data, or changes an API signature
- Touches privacy, compliance, or core data

Example recommendation:

```text
Recommendation: FULL - changes an API signature, so the risk check forces FULL.
```

### Step 3: Classify Complexity

Only classify complexity after risk checks are clear.

Use `LIGHT` when there are no risk hits and the work is low complexity:
- config change
- bugfix
- single-file change

Use `FULL` when there are no risk hits but the work is high complexity:
- new module
- multiple files or multi-file behavior
- crosses frontend/backend boundaries

If risk or complexity is ambiguous, uncertain, or doubtful, escalate one level. A doubtful LIGHT becomes FULL, and the reason says uncertainty caused the escalation.

### Step 4: Ask For Confirmation Or Override

Present the recommendation and one-line reason, then wait for the user to confirm or override before any spec or code work starts. The user's choice is final.

If a risk hit recommended FULL and the user overrides to LIGHT, proceed LIGHT, but keep the risk hit visible in the conversation and record it in the mini-spec's Out of Scope or Notes.

### Step 5: Route

#### FULL Route

Hand off to the existing chain unchanged:

```text
brainstorm -> write-specs -> spec-driven-tdd
```

Do not duplicate brainstorming, writing-specs, or spec-driven-tdd steps inside the router.

#### LIGHT Route

Write `docs/specs/<feature>/mini.md`, get user approval of the scenarios, then dispatch Codex using the standard format with the spec directory path.

Mini-spec shape:

```markdown
---
mode: light
feature: <feature-name>
date: YYYY-MM-DD
---

# <Feature> - Mini Spec

Intent: <one sentence>

## Scenarios

### <Behavior Name>
GIVEN ...
WHEN ...
THEN ...

## Out of Scope
- <exclusion or risk note>
```

Rules:
- Include 2-5 GIVEN/WHEN/THEN scenarios.
- Get user approval before dispatch.
- Record any overridden risk hit in Out of Scope or Notes.

Standard dispatch format:

```text
Use superpowerwithcodex:spec-driven-tdd

Spec directory: docs/specs/<feature>/
Implement in: <paths>
Tests in: <paths>
Test command: <test command>
```

### No Zero-Spec Channel

If the user says the change is urgent and asks to skip specs entirely, still produce `mini.md` before any implementation code. No route skips scenarios.

## Output Template

```text
Recommendation: LIGHT|FULL - <one-line reason>.

Confirm LIGHT|FULL, or override?
```

After confirmation:

```text
Confirmed: LIGHT|FULL.
Next: <mini.md approval and Codex dispatch | brainstorm/write-specs chain>.
```

## Integration

**Called by:**
- Prompt-submit rules before feature work
- Human request when choosing spec workflow weight

**Routes to:**
- `superpowerwithcodex:brainstorming` and `superpowerwithcodex:writing-specs` for FULL
- `superpowerwithcodex:spec-driven-tdd` after LIGHT mini-spec approval

**Produces:**
- A confirmed route and reason
- For LIGHT, `docs/specs/<feature>/mini.md`
