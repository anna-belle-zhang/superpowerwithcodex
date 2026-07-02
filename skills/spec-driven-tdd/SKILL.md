---
name: spec-driven-tdd
description: "Use when dispatched by Claude with a spec directory path - read specs first (specs have specifics intuition misses), write plan, TDD loop per task (unit tests from GIVEN/WHEN/THEN, implement, integration tests), save progress.md with spec fingerprint. Re-entry: verify spec fingerprint before trusting [x] tasks, reopen tasks whose scenarios changed, resume from incomplete tasks."
---

# Spec-Driven TDD

## Overview

Specs have specifics that intuition misses: exact endpoint paths, exact response shapes, exact error messages, exact status codes. Your JWT knowledge says `/api/auth/login` — the spec says `/auth/login`. Read specs first. Always.

**Violating the letter of these rules is violating the spirit.**

## Installation

This skill is installed at `~/.codex/superpowerwithcodex/skills/spec-driven-tdd/SKILL.md`.
Activated when dispatch prompt says: `Use superpowerwithcodex:spec-driven-tdd`

## Process

### Step 0: Detect Test Command

If the dispatch prompt does not specify a test command, auto-detect:
- `package.json` present → `npm test`
- `pytest.ini` or `pyproject.toml` with `[tool.pytest]` → `pytest`
- `Makefile` with `test` target → `make test`
- Otherwise: ask Claude before proceeding

### Step 1: Read All Specs

```bash
cat docs/specs/<feature>/specs/*-delta.md
```

Extract every GIVEN/WHEN/THEN. Each one is a contractual requirement — not a suggestion, not a guideline. If the spec says `{ error: "Unauthorized" }`, your test asserts exactly `{ error: "Unauthorized" }`.

### Step 2: Write Plan → save to `progress.md`

Group scenarios into tasks. Record the spec fingerprint — the hashes of every spec file your plan is derived from:

```bash
cd docs/specs/<feature>/ && sha256sum proposal.md design.md specs/*-delta.md
```

(Use `shasum -a 256` if `sha256sum` is unavailable.) Save to `docs/specs/<feature>/progress.md`:

```markdown
## Spec Fingerprint
<one line per file: hash  path, verbatim sha256sum output>

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
4. **Annotate any compromise** — if you took a coverage shortcut, mocked a path that should be live, or deferred an edge case:
   - Add a `DEBT:` comment at the code site using the file's native comment syntax (`# DEBT:` Python, `// DEBT:` JS/Java, `-- DEBT:` SQL)
   - Add an entry under `## Issues` in `progress.md` describing the compromise
5. **Update progress.md**: `[ ]` → `[x]`, add commit hash

### Step 4: Re-entry (progress.md exists)

If `docs/specs/<feature>/progress.md` already exists:

1. **Verify the spec fingerprint FIRST** — before trusting any `[x]`:
   ```bash
   cd docs/specs/<feature>/ && sha256sum proposal.md design.md specs/*-delta.md
   ```
   Compare against the `## Spec Fingerprint` section in progress.md.
2. **Fingerprint matches** → every `[x]` is trusted. Resume from first incomplete task.
3. **Fingerprint differs (or section is missing)** → progress.md is STALE. The specs changed after those tasks were completed. `[x]` means "done against the OLD spec", which is not done:
   - Diff the changed spec files (`git diff` if committed, otherwise re-read them)
   - For every `[x]` task whose scenarios changed: flip it back to `[ ]`, re-derive its tests from the new scenarios, and verify or fix the existing implementation against them
   - Update the `## Spec Fingerprint` section to the new hashes
   - Then resume from the first incomplete task

A `[x]` from a stale fingerprint is a claim about a contract that no longer exists. Do not resume on top of it — even if the remaining tasks look unrelated to the change, and even if the dispatch note says completed tasks were reviewed and signed off. Sign-off happened against the old spec too.

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
| "Tasks marked [x] are signed off — not my problem" | [x] is relative to the spec version in the fingerprint. Fingerprint mismatch reopens affected tasks; sign-off against an old spec proves nothing about the new one. |
| "Remaining tasks don't touch the changed scenario, so I can skip the check" | You only know which tasks a change touches AFTER diffing the specs. Check the fingerprint first. |

## Red Flags — STOP

- Starting implementation before reading spec files
- Writing tests without first reading GIVEN/WHEN/THEN
- Implementing then testing
- Skipping progress.md
- Resuming from progress.md without recomputing and comparing the spec fingerprint
- Making a compromise (coverage shortcut, mocked path, deferred edge case) without a `DEBT:` annotation at the code site and an Issues entry in progress.md

**All of these mean: read the specs first.**
