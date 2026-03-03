---
name: spec-driven-tdd
description: "Use when dispatched by Claude with a spec directory path - read specs first (specs have specifics intuition misses), write plan, TDD loop per task (unit tests from GIVEN/WHEN/THEN, implement, integration tests), save progress.md. Re-entry: check progress.md, resume from incomplete tasks."
---

# Spec-Driven TDD

## Overview

Specs have specifics that intuition misses: exact endpoint paths, exact response shapes, exact error messages, exact status codes. Your JWT knowledge says `/api/auth/login` — the spec says `/auth/login`. Read specs first. Always.

**Violating the letter of these rules is violating the spirit.**

## Installation

This skill is installed at `~/.codex/superpowerwithcodex/skills/spec-driven-tdd/SKILL.md`.
Activated when dispatch prompt says: `Use superpowerwithcodex:spec-driven-tdd`

## Process

### Step 1: Read All Specs

```bash
cat docs/specs/<feature>/specs/*-delta.md
```

Extract every GIVEN/WHEN/THEN. Each one is a contractual requirement — not a suggestion, not a guideline. If the spec says `{ error: "Unauthorized" }`, your test asserts exactly `{ error: "Unauthorized" }`.

### Step 2: Write Plan → save to `progress.md`

Group scenarios into tasks. Save to `docs/specs/<feature>/progress.md`:

```markdown
## Plan
- [ ] Task 1: [scenario group name]
- [ ] Task 2: [scenario group name]

## Issues
(empty)

## Commits
(empty)
```

### Step 3: TDD Loop Per Task

For each task:

1. **Write failing test** derived from GIVEN/WHEN/THEN (RED)
   - Assert the exact values from the spec
   - Run test — verify it FAILS before implementing
2. **Write minimal implementation** to make test pass (GREEN)
3. **If task involves external calls** — write integration test, verify passes
4. **Update progress.md**: `[ ]` → `[x]`, add commit hash

### Step 4: Re-entry (progress.md exists)

If `docs/specs/<feature>/progress.md` already exists:
1. Read it — find tasks with `[ ]` or failed status
2. If specs changed: re-derive only affected tasks from changed scenarios
3. Resume from first incomplete task

## Why Specs Beat Intuition

Without reading specs, you implement your assumptions:
- You use `/api/auth/login` — spec says `/auth/login`
- You return `{ token, expiresIn }` — spec says `{ token }` only
- You use `{ message: "Forbidden" }` — spec says `{ error: "Unauthorized" }`

All three pass your implementation's own tests. All three fail against the spec.

## Common Violations

| Excuse | Reality |
|--------|---------|
| "I already understand the feature from the prompt" | The prompt is a summary. The spec is the contract. |
| "Reading specs wastes time" | Wrong spec = wasted implementation. Reading takes 2 min. |
| "I'll implement then write tests" | Tests written after pass by construction. They verify what you did, not what was required. |

## Red Flags — STOP

- Starting implementation before reading spec files
- Writing tests without first reading GIVEN/WHEN/THEN
- Implementing then testing
- Skipping progress.md

**All of these mean: read the specs first.**
