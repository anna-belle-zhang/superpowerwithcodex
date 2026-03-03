# Claude-Codex Specs TDD Design

**Date:** 2026-03-03
**Status:** Design Complete — Ready for Specs
**Goal:** Clean role separation where Claude owns specs + E2E validation and Codex owns planning + TDD implementation

---

## 1. Motivation

The existing `codex-subagent-driven-development` skill has Claude writing tests before dispatching Codex for implementation. This conflates two roles: Claude acts as both test author and orchestrator.

This design separates responsibilities cleanly:
- **Claude** is the architect and validator (specs, E2E, spec coverage)
- **Codex** is the planner and implementer (plan, unit tests, integration tests, code)

Codex derives tests directly from specs rather than receiving pre-written tests from Claude. Codex also writes its own implementation plan — Claude never reviews it.

---

## 2. Architecture

### Role Split

| Responsibility | Agent |
|---|---|
| Write specs (GIVEN/WHEN/THEN scenarios) | Claude |
| Dispatch Codex with spec path | Claude |
| Run E2E tests | Claude |
| Validate spec coverage | Claude |
| Read specs from path | Codex |
| Write implementation plan | Codex |
| TDD loop (unit tests → implement → integration tests) | Codex |
| Save `progress.md` in specs folder | Codex |

### Key Differences from `codex-subagent-driven-development`

- Claude does **not** write unit or integration tests — Codex derives them from specs
- Codex writes the implementation plan autonomously — Claude never reviews it
- No Ralph Loop — single MCP dispatch, Claude picks up after Codex returns
- Specs are the contract — Codex treats each GIVEN/WHEN/THEN as inviolable

### Connection

Claude dispatches via `codex-as-mcp` MCP with the spec directory path. Codex's native skill (`superpowerwithcodex:spec-driven-tdd`) activates, handles everything internally, and returns when done.

---

## 3. New Artifacts

Two new skills in `skills/`:

```
skills/
  claude-codex-specs-tdd/
    SKILL.md          ← Claude Code skill
  spec-driven-tdd/
    SKILL.md          ← Codex native skill
```

Both ship in this repo. When users install `superpowerwithcodex`:
- Claude Code picks up `claude-codex-specs-tdd` via plugin skill discovery
- Codex picks up `spec-driven-tdd` via `~/.codex/superpowerwithcodex/skills/`

---

## 4. Claude Code Skill (`claude-codex-specs-tdd`)

### Two Entry Modes

**Fresh entry** (no specs yet):
1. Write specs using `superpowerwithcodex:write-specs` → `docs/specs/<feature>/`
2. Dispatch Codex with spec path (single MCP call)
3. Run E2E tests after Codex returns
4. Validate spec coverage using `superpowerwithcodex:verify-specs`

**Mid-cycle re-entry** (specs already exist, something failed):
1. Read `progress.md` to understand what Codex completed
2. Diagnose: E2E failure? Spec gap? Implementation bug?
3. Choose path:
   - **Fix path** — re-dispatch Codex with failure details + spec path
   - **Spec change path** — update specs, re-dispatch Codex (affected tasks only)
4. Re-run E2E → re-validate

**Entry mode detection:** if `docs/specs/<feature>/` already exists → mid-cycle re-entry, skip spec writing.

### Dispatch Prompt to Codex (minimal)

```
Use superpowerwithcodex:spec-driven-tdd

Spec directory: docs/specs/<feature>/
Implement in: src/
Tests in: tests/
Test command: npm test
```

### After Codex Returns

- Read `progress.md` for summary
- Run E2E tests (auto-detect strategy from project type)
- Run `verify-specs` to check all GIVEN/WHEN/THEN scenarios are covered
- If issues: re-enter mid-cycle

---

## 5. Codex Native Skill (`spec-driven-tdd`)

### Installation Path

```
~/.codex/superpowerwithcodex/skills/spec-driven-tdd/SKILL.md
```

Installed when user clones this repo into `~/.codex/superpowerwithcodex/`. Bootstrap via `.codex/superpowerwithcodex-bootstrap.md`.

### Activates When

Dispatch prompt references `superpowerwithcodex:spec-driven-tdd`.

### Process: First Entry (no `progress.md`)

1. Read all delta specs in the spec directory
2. Parse each GIVEN/WHEN/THEN — treat as contractual requirement
3. Write implementation plan (task per scenario group)
4. Save plan to `progress.md` with task status `pending`
5. Execute TDD loop per task

### Process: Re-entry (`progress.md` exists)

1. Read `progress.md` — find pending or failed tasks
2. If specs changed since last run → re-derive affected tasks only
3. Resume TDD loop from first incomplete task

### TDD Loop Per Task

1. Write failing unit test derived from GIVEN/WHEN/THEN
2. Verify test fails (RED)
3. Write minimal implementation to pass (GREEN)
4. If task involves external dependencies → write integration test → verify passes
5. Update `progress.md`: task → `done`

### `progress.md` Structure

```markdown
## Plan
- [x] Task 1: description
- [ ] Task 2: description

## Issues
- Task 2 failed: [reason and test output]

## Commits
- abc1234: Task 1 implementation
```

### Why Native Skill Over Prompt Injection

Claude's dispatch stays short and stable across all uses. TDD discipline, spec-contract enforcement, and progress tracking live in Codex's environment permanently — not re-stated in every dispatch prompt.

---

## 6. Data Flow

```
docs/specs/<feature>/
  specs/
    <component>-delta.md     ← Claude writes (GIVEN/WHEN/THEN)
  progress.md                ← Codex writes/updates
```

### Sequence

```
Claude: write-specs → docs/specs/<feature>/specs/
Claude: dispatch Codex → spec directory path
  Codex: read specs
  Codex: write plan → progress.md
  Codex: TDD loop (unit → implement → integration)
  Codex: update progress.md per task
  Codex: return
Claude: read progress.md
Claude: run E2E tests
Claude: verify-specs → all scenarios covered?
  If issues → mid-cycle re-entry (fix or update specs)
  If passing → done
```

---

## 7. Codex Install Path Updates

The existing `.codex/` files reference the original `obra/superpowers` namespace. These need updating:

| Current | Updated |
|---|---|
| `~/.codex/superpowers/` | `~/.codex/superpowerwithcodex/` |
| `.codex/superpowers-bootstrap.md` | `.codex/superpowerwithcodex-bootstrap.md` |
| `superpowers:skill-name` | `superpowerwithcodex:skill-name` |

This is a prerequisite for `spec-driven-tdd` to be discoverable by Codex.

---

## 8. Implementation Plan

### Phase 1: Fix Codex Install Namespace
1. Update `.codex/INSTALL.md` — replace `superpowers` paths with `superpowerwithcodex`
2. Create `.codex/superpowerwithcodex-bootstrap.md` (updated from `superpowers-bootstrap.md`)

### Phase 2: Codex Native Skill
1. Create `skills/spec-driven-tdd/SKILL.md`
2. Test with Codex subagent: verify skill activates and follows TDD process

### Phase 3: Claude Code Skill
1. Create `skills/claude-codex-specs-tdd/SKILL.md`
2. Test: fresh entry → mid-cycle re-entry → E2E phase

### Phase 4: Integration Testing
1. End-to-end test with a real feature
2. Verify specs → Codex plan → TDD → E2E cycle completes

---

## Success Criteria

- Claude dispatches Codex with spec path only (no test code in prompt)
- Codex derives unit and integration tests from GIVEN/WHEN/THEN scenarios
- `progress.md` accurately reflects plan and task status after Codex run
- Mid-cycle re-entry correctly identifies affected tasks when specs change
- Codex skill discoverable via `superpowerwithcodex:spec-driven-tdd` without extra setup
