# Quickstart: Codex Subagent-Driven Development Workflow

Complete guide to installing Superpowers, setting up skills, and using the codex-subagent-driven-development workflow for TDD with Codex.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Setting Up Skills](#setting-up-skills)
4. [Creating Your First Project](#creating-your-first-project)
5. [Running the Workflow](#running-the-workflow)
6. [Understanding the Output](#understanding-the-output)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **Claude Code CLI** installed and configured
- **Codex CLI** installed and authenticated (`codex login`)
- **Git** installed
- **Python 3.8+** (for Python projects) or relevant runtime for your language
- **pytest** installed (`pip install pytest` for Python projects)

---

## Installation

### Step 1: Install Superpowers Plugin

Install the Superpowers plugin at **project scope** (recommended for project-specific workflows):

```bash
claude plugin install superpowers@superpowerwithcodex --scope project
```

**What this does:**
- Installs the Superpowers plugin from the `superpowerwithcodex` marketplace
- Scopes to current project (creates `.claude-plugin/` directory)
- Makes skills and commands available in this project

**Verify installation:**
```bash
claude /help
```

You should see:
```
/superpowers:brainstorm - Interactive design refinement
/superpowers:write-plan - Create implementation plan
/superpowers:execute-plan - Execute plan in batches
```

### Step 2: Configure Codex MCP Server

Create or update `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "codex-subagent": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}
```

**What this does:**
- Registers Codex as an MCP server that Claude can call
- Enables the `codex-subagent-driven-development` workflow
- Allows Codex to implement code while Claude writes tests

**Verify Codex is available:**
```bash
codex --version
```

---

## Setting Up Skills

### Understanding Skills

**Skills** are composable workflows that enforce systematic processes:
- `brainstorming` - Refine ideas before coding
- `writing-plans` - Create detailed implementation plans
- `codex-subagent-driven-development` - TDD workflow with Codex
- `test-driven-development` - Enforce RED-GREEN-REFACTOR
- `requesting-code-review` - Review code between tasks

Skills auto-activate based on context. You can also invoke them explicitly.

### Skill Auto-Activation

The `codex-subagent-driven-development` skill activates when:
1. You have a written implementation plan
2. The plan specifies `execution-strategy: codex-subagents`
3. Codex MCP is configured

You can also load it explicitly:
```bash
# In Claude Code session
User: "Load the codex-subagent-driven-development skill"
```

### Personal Skills (Optional)

Create personal skills in `~/.claude/skills/` to customize workflows. These shadow built-in skills.

---

## Creating Your First Project

Follow the **Superpowers workflow** to build a simple Python calculator as a test:

### Step 1: Brainstorming

Start with design before code:

```bash
# In Claude Code session
/superpowers:brainstorm Design a simple Python calculator module
```

**What happens:**
1. Claude asks questions to understand requirements
2. Explores 2-3 different approaches
3. Presents design in sections for validation
4. Saves design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
5. Commits design document

**Key questions Claude will ask:**
- Scope (minimal vs comprehensive)
- Project structure
- Testing framework
- Error handling approach

**Example answers:**
- **Scope:** Minimal (4 operations: add, subtract, multiply, divide)
- **Structure:** Mirror existing patterns (`src/utils/`, `tests/utils/`)
- **Testing:** pytest
- **Error handling:** Division by zero only (YAGNI)

### Step 2: Writing the Plan

After design approval, create implementation plan:

```bash
/superpowers:write-plan Create implementation plan for Python calculator
```

**What happens:**
1. Reads the design document
2. Creates bite-sized tasks (2-5 minutes each)
3. Includes exact file paths, complete code, verification steps
4. Saves to `docs/plans/YYYY-MM-DD-<feature>.md`
5. Offers execution strategy choice

**Plan structure:**
```markdown
---
execution-strategy: codex-subagents
created: YYYY-MM-DD
codex-available: true
---

# Feature Implementation Plan

## Task 1: Setup
- Create directories
- Create __init__.py files
- Verify pytest works

## Task 2: Add/Subtract (RED-GREEN-REFACTOR)
- Step 1: Write failing tests
- Step 2: Run tests (verify RED)
- Step 3: Codex implements
- Step 4: Run tests (verify GREEN)
- Step 5: Code review
- Step 6: Commit

## Task 3: Multiply (RED-GREEN-REFACTOR)
...
```

### Step 3: Choose Execution Strategy

When prompted:
```
Plan complete. Choose execution strategy:

A) Codex subagents (default) - Claude writes tests, Codex implements, Claude reviews
B) Claude subagents (this session) - Fresh subagent per task, fast iteration
C) Parallel session (separate) - Batch execution with checkpoints
```

**Choose A for this tutorial** - tests the codex-subagent workflow.

---

## Running the Workflow

### Automatic Execution

Once you choose **Option A (Codex subagents)**, the workflow executes automatically:

#### Phase 1: Load Plan and Create Todos

```
Step 1: Load Plan and Confirm Execution Strategy
✓ Execution strategy confirmed: codex-subagents

Step 2: Create TodoWrite
✓ Created 5 tasks:
  1. Task 1: Project setup
  2. Task 2: Add and subtract operations
  3. Task 3: Multiply operation
  4. Task 4: Divide operation with error handling
  5. Final verification
```

#### Phase 2: Execute Tasks (TDD Loop)

For each task, the workflow follows **RED-GREEN-REFACTOR**:

**Task Example: Add and Subtract Operations**

```
Task 2: Add and Subtract Operations [in_progress]

Step 3a: RED - Claude writes failing tests
✓ Created tests/utils/test_calculator.py
✓ Tests fail with ModuleNotFoundError (expected)
✓ Committed tests

Step 3b: GREEN - Codex implements
✓ Dispatching Codex subagent...
✓ Codex created src/utils/calculator.py
✓ Implemented add() and subtract()

Step 3c: Verify tests
✓ Running tests...
✓ test_add PASSED
✓ test_subtract PASSED

Step 3d: Code review and boundary enforcement
✓ Only calculator.py modified (no test files)
✓ Dispatching code-reviewer subagent...
✓ Review: APPROVED - No blocking issues

Step 3e: Commit and continue
✓ Committed implementation
✓ Task 2 complete
```

This repeats for Tasks 3, 4, and Final Verification.

### What's Happening Behind the Scenes

**Claude's Role:**
- Writes tests first (RED phase)
- Runs tests to verify they fail
- Commits tests only
- Dispatches Codex for implementation
- Reviews Codex's code
- Enforces file boundaries
- Manages git commits

**Codex's Role:**
- Reads tests to understand requirements
- Implements minimal code to pass tests
- Follows file boundaries (read-only vs writable)
- Returns control to Claude for verification

**File Boundaries:**
```
Implement in:  src/utils/calculator.py
Read only:     tests/utils/test_calculator.py
               pytest.ini
               __init__.py files
```

Codex **cannot** modify test files - boundary enforcement prevents test pollution.

### Retry Chain

If tests fail or code review finds issues:

```
Retry Chain (automatic):
1. Codex retry 1: Send failing output + guidance
2. Codex retry 2: Add "research required" guidance
3. Claude fix 1: Claude implements manually
4. Claude fix 2: Claude researches + fixes
5. Human escalation: Ask user to fix/skip/revise plan
```

---

## Understanding the Output

### Git History

Clean commit history from TDD workflow:

```bash
git log --oneline
```

```
d9d5499 Feat: Add division operation with error handling
f5dca16 Test: Add tests for divide operation with error handling
cad39c7 Feat: Add multiplication operation
ee123d8 Test: Add test for multiply operation
3ed0286 Feat: Add addition and subtraction operations
a8d14c9 Test: Add tests for add and subtract operations
7c51a36 Setup: Python project structure and pytest config
98fc695 Design: Python calculator module for testing codex-subagent workflow
```

**Pattern:** Test commit → Implementation commit (per task)

### File Structure

```
project/
├── .mcp.json                           # Codex MCP server config
├── pytest.ini                          # pytest configuration
├── src/
│   ├── __init__.py                    # Package marker
│   └── utils/
│       ├── __init__.py                # Package marker
│       └── calculator.py              # Implementation (by Codex)
├── tests/
│   └── utils/
│       ├── __init__.py                # Package marker
│       └── test_calculator.py         # Tests (by Claude)
└── docs/
    └── plans/
        ├── YYYY-MM-DD-calculator-design.md     # Design doc
        └── YYYY-MM-DD-calculator.md            # Implementation plan
```

### Test Output

```bash
PYTHONPATH=. pytest tests/utils/test_calculator.py -v
```

```
tests/utils/test_calculator.py::test_add PASSED              [ 20%]
tests/utils/test_calculator.py::test_subtract PASSED         [ 40%]
tests/utils/test_calculator.py::test_multiply PASSED         [ 60%]
tests/utils/test_calculator.py::test_divide PASSED           [ 80%]
tests/utils/test_calculator.py::test_divide_by_zero PASSED   [100%]

============================== 5 passed in 0.32s ==============================
```

### Code Quality

**Type hints and docstrings:**
```python
def divide(a: float, b: float) -> float:
    """Return ``a`` divided by ``b``; raise ``ValueError`` if ``b`` is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**Error handling:**
```python
def test_divide_by_zero():
    """Test that division by zero raises ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

---

## Calling Codex Subagent Directly (Advanced)

### Via MCP Tool

You can call Codex directly for one-off tasks:

```python
# In Claude Code session, use the MCP tool
mcp__codex-subagent__spawn_agent(
    prompt="""
    Task: Implement a fibonacci function

    File boundaries:
    - Implement in: src/utils/math.py
    - Read only: tests/

    Requirements:
    1. Create fibonacci(n: int) -> int
    2. Include type hints and docstring
    3. Handle n < 0 by raising ValueError

    Verification:
    Run: pytest tests/utils/test_math.py -v
    """
)
```

### Parallel Codex Agents

For independent tasks:

```python
mcp__codex-subagent__spawn_agents_parallel(
    agents=[
        {"prompt": "Implement add() in src/utils/calculator.py"},
        {"prompt": "Implement subtract() in src/utils/calculator.py"},
        {"prompt": "Implement multiply() in src/utils/calculator.py"}
    ]
)
```

**When to use:**
- Tasks have no dependencies
- Can run simultaneously
- Share same file boundaries

---

## Troubleshooting

### Issue: "Agent type 'codex-subagent' not found"

**Cause:** Codex MCP not configured or not available.

**Fix:**
1. Check `.mcp.json` exists and has correct config
2. Verify Codex CLI is installed: `codex --version`
3. Verify Codex is authenticated: `codex login`
4. Restart Claude Code session

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause:** Python can't find the `src` package.

**Fix:**
1. Ensure `src/__init__.py` exists
2. Run pytest with PYTHONPATH: `PYTHONPATH=. pytest tests/`
3. Or create `pyproject.toml` with package config
4. Or install package in editable mode: `pip install -e .`

### Issue: Tests fail after Codex implementation

**Cause:** Codex misunderstood requirements or tests are unclear.

**Fix:**
- Workflow automatically enters retry chain
- Retry 1: Claude sends failing output to Codex
- Retry 2: Claude adds detailed guidance
- Retry 3+: Claude implements manually
- You can also revise tests and re-run

### Issue: Codex modified test files

**Cause:** Boundary violation (should not happen - skill enforces boundaries).

**Fix:**
- Workflow automatically detects boundary violations
- Reverts unauthorized changes
- Retries with stronger boundary instructions
- Reports to you if retry fails

### Issue: Code review finds critical issues

**Cause:** Codex implementation has bugs or doesn't match requirements.

**Fix:**
- Workflow automatically enters retry chain
- Feeds review issues back to Codex
- Retries implementation
- Escalates to you after max retries

### Issue: Skill doesn't auto-activate

**Cause:** Plan doesn't specify `execution-strategy: codex-subagents`.

**Fix:**
1. Edit plan file to add YAML frontmatter:
   ```yaml
   ---
   execution-strategy: codex-subagents
   codex-available: true
   ---
   ```
2. Or explicitly load skill: "Use codex-subagent-driven-development"

---

## Next Steps

### Extend the Calculator

Add more features to practice the workflow:

```bash
/superpowers:brainstorm Add power and square root operations to calculator
```

Follow the same process:
1. Brainstorm → Design
2. Write Plan → Choose Codex subagents
3. Execute → TDD cycle with Codex
4. Verify → All tests pass

### Try Other Languages

The workflow works with any language:

**JavaScript/TypeScript:**
- Testing: Jest, Vitest
- Codex implements in `src/`, Claude tests in `tests/`

**Rust:**
- Testing: `cargo test`
- Codex implements in `src/`, Claude tests in `tests/`

**Go:**
- Testing: `go test ./...`
- Codex implements in `*.go`, Claude tests in `*_test.go`

### Explore Other Workflows

**Subagent-Driven Development (without Codex):**
```bash
/superpowers:write-plan <task>
# Choose option B: Claude subagents
```

**Parallel Batch Execution:**
```bash
/superpowers:execute-plan
# Choose option C: Parallel session
```

**Manual TDD (you write everything):**
- Follow `test-driven-development` skill
- No subagents, full control

---

## Summary

**Complete workflow recap:**

```bash
# 1. Install plugin (one-time setup)
claude plugin install superpowers@superpowerwithcodex --scope project

# 2. Configure Codex MCP (one-time setup)
# Create .mcp.json with codex-subagent server

# 3. Design phase
/superpowers:brainstorm <idea>
# Answer questions, validate design

# 4. Planning phase
/superpowers:write-plan <feature>
# Choose execution strategy: A (Codex subagents)

# 5. Execution phase (automatic)
# - Claude writes tests (RED)
# - Codex implements (GREEN)
# - Claude reviews (REFACTOR)
# - Repeat for all tasks

# 6. Verification
# - All tests pass
# - Clean git history
# - Code review approved

# 7. Completion
# - Push to remote or merge to main
# - Clean up worktree
```

**Key principles:**
- **Design before code** - brainstorming → planning → implementation
- **Tests before implementation** - RED → GREEN → REFACTOR
- **Boundary enforcement** - Codex can't modify tests
- **Code review between tasks** - catch issues early
- **Clean git history** - test commit → implementation commit

**What makes this workflow powerful:**
1. **Separation of concerns:** Claude writes requirements (tests), Codex implements
2. **Quality gates:** Tests must fail, then pass; code review must approve
3. **Systematic process:** Can't skip steps, enforced workflow
4. **Context isolation:** Codex execution doesn't pollute main conversation
5. **Failure recovery:** Automatic retry chains with escalation

---

## Resources

**Documentation:**
- Main README: `README.md`
- Codex integration: `docs/codex-integration.md`
- Skills guide: `skills/writing-skills/SKILL.md`
- TDD guide: `skills/test-driven-development/SKILL.md`

**Example Projects:**
- This calculator: `docs/plans/2025-12-29-python-calculator.md`
- JavaScript example: `src/utils/math.js`

**Get Help:**
```bash
/help  # Built-in commands
```

**Report Issues:**
https://github.com/anna-belle-zhang/superpowerwithcodex/issues

---

**Ready to build systematically? Start with `/superpowers:brainstorm`!** 🚀
