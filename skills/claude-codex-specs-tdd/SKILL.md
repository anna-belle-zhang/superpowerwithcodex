---
name: claude-codex-specs-tdd
description: Use when implementing features with Codex as implementer - Claude writes specs (GIVEN/WHEN/THEN), dispatches Codex with spec path, Codex plans+tests+implements autonomously, Claude runs E2E and validates. NOT for writing tests yourself before dispatching Codex.
---

# Claude-Codex Specs TDD

## Overview

Claude is architect and validator. Codex is planner and implementer. Specs are the contract — Codex derives all tests from them. Claude never writes unit or integration tests.

**Violating the letter of these rules is violating the spirit.**

## The Full Workflow

```
1. Brainstorm   → use superpowerwithcodex:brainstorming
2. Write specs  → use superpowerwithcodex:write-specs → docs/specs/<feature>/
3. Dispatch     → send spec path to Codex (format below)
4. Codex runs   → loads spec-driven-tdd, reads specs, writes plan,
                   TDD loop, updates progress.md
5. E2E tests    → Claude runs E2E after Codex returns
6. Validate     → use superpowerwithcodex:verify-specs
```

## When to Use

- Implementing features with Codex via MCP
- Specs exist OR need to be written first
- You want Codex to plan AND test AND implement autonomously

**When NOT to use:**
- Codex plugin not installed → use `subagent-driven-development`
- Need human review between tasks → use `codex-subagent-driven-development`

## The Two Entry Modes

**Detect automatically:**
- `docs/specs/<feature>/` does NOT exist → Fresh entry
- `docs/specs/<feature>/` exists → Mid-cycle re-entry

### Fresh Entry

1. Write specs: use `superpowerwithcodex:write-specs` → `docs/specs/<feature>/`
2. Dispatch Codex (see format below)
3. Run E2E tests after Codex returns
4. Validate: use `superpowerwithcodex:verify-specs`

### Mid-Cycle Re-entry (specs already exist)

1. Read `docs/specs/<feature>/progress.md` — understand what Codex completed
2. **Check staleness**: recompute `sha256sum proposal.md design.md specs/*-delta.md` (from the feature dir) and compare with progress.md's `## Spec Fingerprint` section
   - Mismatch or missing section → specs changed after Codex's last run. Tell the user which files changed; Codex will reopen affected `[x]` tasks on re-entry (per spec-driven-tdd). Never present `[x]` tasks from a stale fingerprint as verified work.
3. Diagnose: E2E failure? Spec gap? Bug?
4. Choose:
   - **Fix**: re-dispatch Codex with failure + spec path
   - **Spec change**: update affected scenarios, re-dispatch Codex

When specs change: Codex re-runs only affected tasks, not the full plan.

## Dispatch Format

**Gate: validate specs before every dispatch (fresh or re-entry):**

```bash
python scripts/validate_specs.py docs/specs/<feature>/
```

Non-zero exit → fix the reported spec defects first. Never dispatch Codex on specs that fail validation — a malformed contract wastes an entire Codex cycle. (If the script does not exist in this checkout, note that and proceed.)

```
Use superpowerwithcodex:spec-driven-tdd

Spec directory: docs/specs/<feature>/
Implement in: src/
Tests in: tests/
Test command: <auto-detect from project, or specify: pytest / npm test / etc.>
```

That is the entire prompt. Do not embed tests, test code, or implementation details.

**Dispatch via:** `codex:codex-rescue` subagent (Agent tool with `subagent_type: codex:codex-rescue`). No MCP server required.

## After Codex Returns

1. Read `docs/specs/<feature>/progress.md`
2. Run E2E tests (auto-detect from project type)
3. Run `superpowerwithcodex:verify-specs`
4. If issues → mid-cycle re-entry

## Common Violations

| Excuse | Reality |
|--------|---------|
| "Specs are optional in this workflow" | Specs are the contract Codex tests derive from. No specs = no contract. |
| "Writing tests is faster than writing specs" | Tests you write = old pattern. Specs let Codex write its own tests. Specs take under 5 minutes. |
| "Specs would take 15-20 minutes" | That estimate is wrong. 3-5 scenarios = under 5 minutes. Verified in practice. |
| "I know what this feature needs" | Specs capture specifics: exact endpoints, exact response shapes, exact error messages. Intuition misses these. |
| "Tests are the demo artifact" | Specs ARE the artifact. Tests are Codex's output, not yours. |
| "Dispatch Codex with a detailed prose prompt" | Prose is ambiguous. GIVEN/WHEN/THEN is a verifiable contract. |

## Red Flags — STOP

You are about to violate this skill if you are:
- Writing test files before dispatching Codex
- Embedding test code in the Codex dispatch prompt
- Dispatching Codex with implementation details instead of a spec path
- Thinking "specs would take too long, I'll just write tests"

**All of these mean: write specs first. Then dispatch with spec path only.**
