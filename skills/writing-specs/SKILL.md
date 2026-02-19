---
name: writing-specs
description: Use when brainstorming is complete and you need structured specifications with testable GIVEN/WHEN/THEN scenarios - transforms design into proposal, design doc, and delta specs that map directly to tests
---

# Writing Structured Specifications

Transform brainstorming output into structured, testable specification artifacts.

**Core principle:** Every behavior change becomes a GIVEN/WHEN/THEN scenario that maps directly to a test.

**Announce at start:** "I'm using the writing-specs skill to create structured specifications."

## Overview

**What this produces:**
```
docs/specs/<feature>/
  proposal.md              # Intent, scope, impact, success criteria
  design.md                # Technical decisions (from brainstorm output)
  specs/
    <component>-delta.md   # Delta spec: ADDED/MODIFIED/REMOVED + scenarios
```

**Living specs directory:** `docs/specs/_living/*.md` — merged source of truth after archiving.

## The Process

### Step 1: Locate the Design

- Check for recent brainstorm output in `docs/plans/YYYY-MM-DD-*-design.md`
- If no design exists, ask: "No design doc found. Run /superpowers:brainstorm first?"
- Read the design document thoroughly before proceeding.

### Step 2: Create Feature Directory

```bash
mkdir -p docs/specs/<feature>/specs
```

Use a short, kebab-case feature name derived from the design topic.

### Step 3: Write proposal.md

```markdown
# <Feature Name> Proposal

## Intent
[What problem this solves and why it matters]

## Scope
**In scope:**
- [Specific deliverable 1]
- [Specific deliverable 2]

**Out of scope:**
- [Explicit exclusion 1]

## Impact
- **Users affected:** [who]
- **Systems affected:** [what components change]
- **Risk:** [low/medium/high + reasoning]

## Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
```

### Step 4: Write design.md

Adapt the brainstorming design doc into a structured format:

```markdown
# <Feature Name> Design

## Architecture
[Key architectural decisions from brainstorm]

## Components
[Components and their responsibilities]

## Data Flow
[How data moves through the system]

## Error Handling
[Error scenarios and handling strategy]

## Dependencies
[External dependencies and integration points]
```

### Step 5: Write Delta Specs

Create one `<component>-delta.md` per component that changes. This is the critical artifact — every behavior maps to a testable scenario.

**Delta spec format:**

```markdown
# <Component Name> Delta Spec

## ADDED

### <Behavior Name>
GIVEN [precondition]
WHEN [action]
THEN [expected result]

### <Another Behavior>
GIVEN [precondition]
WHEN [action]
THEN [expected result]

## MODIFIED

### <Behavior Name>
**Was:** [old behavior]
**Now:** [new behavior]
**Reason:** [why this changed]

GIVEN [precondition]
WHEN [action]
THEN [new expected result]

## REMOVED

### <Behavior Name>
**Was:** [what existed]
**Reason:** [why it's being removed]
```

**Rules for writing scenarios:**
- One scenario per behavior (not per test — a scenario may need multiple test cases)
- GIVEN describes setup/preconditions only
- WHEN describes exactly one action
- THEN describes observable outcomes only
- No implementation details in scenarios (test the what, not the how)
- Each scenario must be independently verifiable

### Step 6: Review and Commit

- Present the specs to the user section by section (like brainstorming)
- Ask after each delta spec: "Does this capture the behavior correctly?"
- Once approved:

```bash
git add docs/specs/<feature>/
git commit -m "spec: add structured specs for <feature>"
```

## Checking for Living Specs

Before writing delta specs, check `docs/specs/_living/` for existing specs on the same components:

- If a living spec exists for a component, review it first
- Use MODIFIED (not ADDED) for behaviors that change existing living spec entries
- Use REMOVED for behaviors in the living spec that this feature eliminates
- Use ADDED only for genuinely new behaviors

## Key Principles

- **Scenarios are contracts** — they define what tests must verify
- **Delta over snapshot** — only specify what changes, not the entire system
- **One component per delta file** — keeps specs focused and reviewable
- **No implementation in specs** — describe behavior, not code
- **Check living specs first** — avoid contradictions with existing system state

## Integration

**Called after:**
- `superpowers:brainstorming` — when user opts in to structured specs

**Consumed by:**
- `superpowers:writing-plans` — plans reference scenarios from delta specs
- `superpowers:codex-subagent-driven-development` — scenarios become Codex contracts
- `superpowers:verifying-specs` — verifies implementation matches specs
- `superpowers:archiving-specs` — merges deltas into living specs
