---
name: writing-plans
description: Use when design is complete and you need detailed implementation tasks for engineers with zero codebase context - creates comprehensive implementation plans with exact file paths, complete code examples, and verification steps assuming engineer has minimal domain knowledge
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After saving the plan, offer execution choice. Prefer Codex subagents when available, otherwise fall back to Claude subagents.

**"Plan complete and saved to `docs/plans/<filename>.md`. Choose execution strategy:**

**A) Codex subagents (default)** - Claude writes tests, Codex implements, Claude reviews (sequential TDD)

**B) Claude subagents (this session)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**C) Parallel session (separate)** - Open a new session with executing-plans, batch execution with checkpoints

**If A (Codex) chosen:**
- If Codex is available:
  - Add plan metadata (recommended):
    - `execution-strategy: codex-subagents`
  - **REQUIRED SUB-SKILL:** Use `superpowers:codex-subagent-driven-development`
- If Codex is NOT available:
  - Inform the user why (missing `.mcp.json`, missing `codex` CLI, etc.)
  - Fall back to B and set `execution-strategy: claude-subagents`

**If B (Claude subagents) chosen:**
- Add plan metadata (recommended):
  - `execution-strategy: claude-subagents`
- **REQUIRED SUB-SKILL:** Use `superpowers:subagent-driven-development`

**If C (Parallel session) chosen:**
- Guide them to open a new session in the worktree
- **REQUIRED SUB-SKILL:** New session uses `superpowers:executing-plans`

## Optional Plan Metadata (Recommended)

If the plan will be executed immediately, include YAML frontmatter at the top of the plan:

```yaml
---
execution-strategy: codex-subagents | claude-subagents
created: YYYY-MM-DD
codex-available: true | false
---
```
