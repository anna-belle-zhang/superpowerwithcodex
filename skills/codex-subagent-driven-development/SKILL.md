---
name: codex-subagent-driven-development
description: Use when executing implementation plans with Codex subagents - Claude writes tests, Codex implements, Claude reviews in sequential TDD workflow with a retry chain and file-boundary protection
---

# Codex Subagent-Driven Development

Execute a plan by having Claude write tests first (TDD), dispatch Codex for implementation, then review/verify with quality gates.

**Core principle:** Claude writes tests (RED) → Codex implements (GREEN) → Claude reviews (REFACTOR) → retry chain if needed

## Overview

**Workflow responsibilities:**
- Claude handles: planning, test writing, running tests, code review, git operations
- Codex handles: implementation only (within explicit file boundaries)

**When to use:**
- You have a clear implementation plan with bite-sized tasks
- You want strict separation between test authoring and implementation
- Codex is configured and available

**When NOT to use:**
- Codex is not available (use `superpowers:subagent-driven-development`)
- The plan needs revision (use `superpowers:brainstorming` first)
- Tasks are tightly coupled and require manual sequencing

## Prerequisites

1. **Codex MCP configured**
   - `.mcp.json` contains an MCP server named `codex-subagent`
   - Codex CLI is installed and authenticated (`codex login`)

2. **A written plan**
   - Saved under `docs/plans/YYYY-MM-DD-<feature>.md`
   - Tasks are small (2–5 minutes each)

## Execution Mode: Sequential by Default

**Default:** Dispatch one Codex subagent at a time using `spawn_agent`. Complete each task's full TDD cycle (RED → GREEN → review → commit) before starting the next task.

**Parallel only on request:** Only use `spawn_agents_parallel` when the user explicitly asks for parallel execution. Parallel dispatch skips the sequential review-between-tasks gate and risks boundary violations across concurrent tasks.

**Why sequential:** Each task may depend on the previous task's output. Code review catches issues early. The retry chain requires sequential feedback loops. Parallel dispatch should be a conscious opt-in, not a default.

## The Process

### 1. Load Plan and Confirm Execution Strategy

- Read the plan file.
- Confirm the plan's execution strategy is `codex-subagents` (or ask user to choose).
- Check Codex availability using the wrapper (`lib/codex-integration.js`).
- If unavailable, offer fallback to `superpowers:subagent-driven-development`.

### 2. Create TodoWrite

Create a TodoWrite list containing every task in the plan.

### 3. Execute Tasks (Sequential TDD Loop)

For each task:

#### Step 3a: RED (Claude writes failing tests)

- Read the task carefully.
- **If the plan references `specs-dir`:** read the delta specs and derive tests from GIVEN/WHEN/THEN scenarios. Each scenario's GIVEN → setup, WHEN → action, THEN → assertion.
- Write the failing test(s) exactly as specified.
- Run the test(s) to confirm failure.
- Commit tests only:
  - `git add <test-files> && git commit -m "Test: <task summary>"`

#### Step 3b: GREEN (Codex implements within boundaries)

- Define explicit file boundaries:
  - **Implement in:** code files Codex may modify
  - **Read only:** tests, configs, lockfiles, `docs/specs/`, etc.
- Build a prompt that includes boundaries and the task steps verbatim.
- **If specs exist:** include a "Specification Contract" section in the Codex prompt listing all GIVEN/WHEN/THEN scenarios from the task's delta spec as inviolable requirements that the implementation must satisfy.
- Dispatch **one** Codex subagent via `spawn_agent` (sequential, the default):
  - `executeWithCodex({ prompt, workingDir, retryCount, onProgress })`
  - **Do NOT use `spawn_agents_parallel`** unless the user explicitly requested parallel execution.
- Wait for the subagent to complete before proceeding to Step 3c.

#### Step 3c: Verify tests

- Run the specified tests (or the smallest relevant suite).
- If tests pass, proceed.
- If tests fail, enter the retry chain.

**Retry chain (recommended default):**
1. Codex retry 1: send failing test output + guidance
2. Codex retry 2: add explicit “research required” guidance + retry
3. Claude fix 1: Claude implements the fix manually
4. Claude fix 2: Claude researches + fixes
5. Human escalation: ask the user whether to fix, skip, or revise plan

#### Step 3d: Code review and boundary enforcement

- Get git SHAs:
  - `BASE_SHA` = test commit SHA
  - `HEAD_SHA` = current HEAD
- Verify file boundaries:
  - If Codex modified any read-only files, revert those changes and retry.
- **If specs exist:** verify all GIVEN/WHEN/THEN scenarios from the task's delta spec are covered by tests. An uncovered scenario is a Critical review issue.
- Dispatch a code-reviewer subagent:
  - Use the template at `skills/requesting-code-review/code-reviewer.md`

If review issues exist, feed them into the retry chain (as `failure_type: review_issues`).

#### Step 3e: Commit and continue

- Commit implementation:
  - `git add <files> && git commit -m "Feat: <task summary>"`
- Mark the task complete in TodoWrite.
- Continue to the next task.

### 4. Final Review

After all tasks:
- Run the full relevant test suite
- Dispatch a final code review for the full diff
- Confirm all plan requirements are met

### 5. Finish

- Announce: “I’m using the finishing-a-development-branch skill to complete this work.”
- **REQUIRED SUB-SKILL:** Use `superpowers:finishing-a-development-branch`

## Integration: Codex Wrapper Library

This workflow expects `superpowers-main/lib/codex-integration.js`:
- `checkCodexAvailability()`
- `executeWithCodex(config)`
- `retryWithFeedback(originalPrompt, feedback, attempt, maxRetries)`
- `detectBoundaryViolations(changedFiles, boundaries)`
- `buildFileBoundaries(task)`
- `formatBoundaryInstructions(boundaries)`

## Required Sub-Skills

- `superpowers:test-driven-development`
- `superpowers:requesting-code-review`
- `superpowers:finishing-a-development-branch`

