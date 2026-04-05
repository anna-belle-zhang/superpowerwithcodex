---
description: Create detailed implementation plan with bite-sized tasks
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

**Specs:** [Path to docs/specs/<feature>/ if structured specs exist, otherwise omit]

---
```

**When structured specs exist** (`docs/specs/<feature>/`), read the delta specs and incorporate scenarios into each task (see Task Structure below).

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Scenarios (from delta spec):** *(include when specs-dir exists)*
| ID | Scenario | Source |
|----|----------|--------|
| S1 | GIVEN x WHEN y THEN z | specs/<component>-delta.md |
| S2 | GIVEN a WHEN b THEN c | specs/<component>-delta.md |

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    # GIVEN x (from S1)
    result = function(input)  # WHEN y
    assert result == expected  # THEN z
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
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Choose execution strategy:**

**A) Codex subagents (default)** - Claude writes tests, Codex implements, Claude reviews (sequential TDD)

**B) Claude subagents (this session)** - Fresh subagent per task, review between tasks

**C) Parallel session (separate)** - Open a new session with execute-plan, batch execution with checkpoints

**D) Ralph-Codex-E2E (autonomous)** - Codex handles dev + unit + integration tests, Claude handles E2E, loops until all tests green
