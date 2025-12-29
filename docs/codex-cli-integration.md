# Codex CLI Integration Guide

Quick guide to using Codex for one-off coding tasks with Superpowers.

---

## Overview

**What this provides:**
- Quick code implementation without full TDD workflow
- File boundary enforcement
- Isolated execution (doesn't pollute main conversation)
- Simple task → implementation → done

**When to use:**
- ✅ Implement single function
- ✅ Fix specific bug
- ✅ Create new file from description
- ✅ Refactor code section
- ❌ Full feature with tests (use codex-subagent-driven-development)

---

## Quick Start

### Install

```bash
# 1. Install Superpowers
claude plugin install superpowers@superpowerwithcodex --scope project

# 2. Configure Codex MCP (in .mcp.json)
{
  "mcpServers": {
    "codex-subagent": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}

# 3. Verify Codex
codex --version
```

### Usage

Just ask with trigger phrases:

```bash
User: Use Codex to implement [feature]
User: Let Codex write [code]
User: Codex create [file]
User: Ask Codex to fix [issue]
```

---

## Examples

### 1. Implement Function

```
User: Use Codex to implement a fibonacci function in src/utils/math.py

Claude: *dispatches Codex with boundaries*

Claude: Codex created fibonacci function in src/utils/math.py

Implementation:
- Recursive with @lru_cache memoization
- Handles negative n (raises ValueError)
- Type hints: def fibonacci(n: int) -> int
- Docstring included

Verification:
- Run: python -c "from src.utils.math import fibonacci; print(fibonacci(10))"
- Expected: 55

Would you like me to write unit tests for this?
```

### 2. Fix Bug

```
User: Codex fix the off-by-one error in api/routes.py:45

Claude: *dispatches with boundary: modify api/routes.py only*

Claude: Codex fixed off-by-one error in api/routes.py:45

Change:
- Old: for i in range(len(items)):
- New: for i, item in enumerate(items):

Used enumerate() for clarity and to ensure all items processed.

Verification:
- Run: pytest tests/test_routes.py
- Expected: All tests pass

Should I commit this fix?
```

### 3. Create File

```
User: Let Codex create a logger utility in src/utils/logger.py

Claude: Codex created logger.py with:
- Configurable log levels
- File and console output
- Log rotation (10MB, 5 backups)
- JSON formatting option

API:
  from src.utils.logger import get_logger
  logger = get_logger(__name__)
  logger.info("message")

Note: Requires python-json-logger. Add to requirements.txt?
```

---

## vs Full TDD Workflow

| Feature | codex-cli | codex-subagent-driven-development |
|---------|-----------|-----------------------------------|
| **Use case** | One-off tasks | Full features |
| **Tests** | You write after (optional) | Claude writes first (mandatory) |
| **Process** | Quick implementation | RED-GREEN-REFACTOR cycle |
| **Scope** | Single function/file | Multiple related tasks |
| **Review** | Optional | Mandatory between tasks |
| **Commits** | Manual/batched | Automatic per task |
| **Planning** | None required | Full plan document |

**Choose codex-cli when:**
- Quick fix needed
- Single function implementation
- File creation
- Small refactoring

**Choose codex-subagent-driven-development when:**
- Building feature end-to-end
- Want TDD discipline
- Multiple related tasks
- Need code review between steps

---

## How It Works

### Architecture

```
User Request
    ↓
codex-cli Skill (recognizes intent, defines boundaries)
    ↓
mcp__codex-subagent__spawn_agent (executes)
    ↓
Codex implements
    ↓
Summary → Main Conversation
```

### File Boundaries

**Always defined:**
- **Writable:** Files Codex can create or modify
- **Read-only:** Files for context (tests, configs)
- **Off-limits:** Files Codex shouldn't touch

**Example:**
```
Boundaries:
- Implement in: src/utils/math.py
- Read only: tests/test_math.py, setup.py
- Off-limits: .git/, .env
```

### Context Isolation

Codex execution happens in isolated context - main conversation stays clean.

---

## Best Practices

### 1. Be Specific

**Vague:**
```
User: Codex write some math functions
```

**Better:**
```
User: Use Codex to implement fibonacci and factorial in src/utils/math.py
      Both should have type hints and handle edge cases
```

### 2. Define Scope

```
User: Codex fix bug in routes.py:45
      Only modify that specific line, don't refactor the whole file
```

### 3. Specify Requirements

```
User: Let Codex create logger.py with:
      - Configurable log levels
      - File rotation
      - JSON format option
```

### 4. Follow Up with Tests

```
User: Use Codex to implement fibonacci

Claude: *implements function*

User: Now write tests for fibonacci

Claude: *writes comprehensive tests*
```

### 5. Combine with Other Skills

**Codex + Code Review:**
```
User: Codex implement feature X
Claude: *implements*
User: Review this code
Claude: *uses requesting-code-review skill*
```

**Codex + Planning:**
```
User: /superpowers:write-plan Implement calculator
Claude: *creates plan*
User: For task 1, use Codex to create the file structure
```

---

## Typical Workflows

### Workflow 1: Quick Feature Addition

```bash
# 1. Implement with Codex
User: Use Codex to add pagination to api/routes.py

# 2. Write tests yourself (or have Claude do it)
User: Write tests for the pagination functionality

# 3. Commit
User: Commit these changes with message "Add pagination to API"
```

### Workflow 2: Bug Fix

```bash
# 1. Identify bug
User: The login function has a race condition in auth.py:78

# 2. Fix with Codex
User: Codex fix the race condition using threading.Lock

# 3. Verify
Claude: *Codex fixes, suggests test command*

# 4. Run tests
User: Run the tests

# 5. Commit if passing
User: Commit the fix
```

### Workflow 3: Create Utility

```bash
# 1. Create with Codex
User: Let Codex create a retry decorator in src/utils/retry.py
      Should support max_retries and backoff

# 2. Test manually
User: Test the retry decorator with a failing function

# 3. Write comprehensive tests
User: Write unit tests for the retry decorator

# 4. Integrate
User: Update API calls to use @retry decorator
```

---

## Troubleshooting

### Skill Doesn't Activate

**Fix:** Use explicit trigger phrase
```
User: Use Codex to implement [specific task]
```

### Boundary Violations

**Symptom:** Codex modifies files it shouldn't

**Fix:** Skill automatically detects and reverts unauthorized changes, then retries with stricter boundaries

### Unclear Requirements

**Symptom:** Codex implements but not what you wanted

**Fix:** Be more specific in your request
```
# Vague
User: Codex add validation

# Specific
User: Codex add email validation using regex pattern
      Must check for @ symbol and domain
      Raise ValueError("Invalid email") if validation fails
```

### MCP Not Configured

**Symptom:** "codex-subagent not found"

**Fix:**
1. Check `.mcp.json` exists with codex-subagent entry
2. Verify Codex CLI: `codex --version`
3. Restart Claude Code session

---

## Comparison: Codex vs Gemini vs Claude

| Task Type | Best Tool | Why |
|-----------|-----------|-----|
| Implement function | **Codex** | Code generation specialist |
| Fix specific bug | **Codex** | Quick focused fixes |
| Analyze image | **Gemini** | Multimodal |
| Scan codebase patterns | **Gemini** | Large-scale analysis |
| Write tests | **Claude** | Reasoning about edge cases |
| Code review | **Claude** | Context + quality analysis |
| Edit existing code | **Claude** | Precise modifications |
| Design architecture | **Claude** (brainstorming) | System thinking |

**Use all three:**
1. **Gemini** - Analyze requirements (from images/docs)
2. **Claude** - Design and plan
3. **Codex** - Implement quickly
4. **Claude** - Write tests and review

---

## Integration with Other Skills

### With TDD

```bash
# Start with TDD workflow for main feature
User: /superpowers:brainstorm Build calculator API

# Use codex-cli for quick utilities
User: During implementation, use Codex to create input validator

# Back to TDD for main code
User: Continue with codex-subagent-driven-development for API endpoints
```

### With Brainstorming

```bash
# Design first
User: /superpowers:brainstorm Design authentication system

# Implement utilities with Codex
User: Codex create password hashing utility
User: Codex create JWT token manager

# Main feature with TDD
User: Now implement authentication with full TDD workflow
```

### With Code Review

```bash
# Implement quickly
User: Use Codex to implement OAuth flow

# Review thoroughly
User: Review the OAuth implementation for security issues

# Fix issues found
User: Codex fix the CSRF vulnerability found in review
```

---

## Cost and Performance

**Codex via MCP:**
- Fast execution (seconds for simple tasks)
- Context-efficient (isolated from main conversation)
- No additional quota beyond Codex CLI limits

**When to batch:**
- Multiple related functions → one Codex call with all requirements
- Series of small fixes → batch in single request if related

**When to separate:**
- Unrelated tasks → separate calls for clarity
- Different file boundaries → separate calls for safety

---

## Limitations

**Codex-cli cannot:**
- Write tests (Claude should do this)
- Do code review (use requesting-code-review skill)
- Handle multi-step features (use codex-subagent-driven-development)
- Make architectural decisions (use brainstorming skill)

**Codex-cli is for:**
- Quick implementations
- Focused fixes
- File creation
- Simple refactoring

---

## Next Steps

### Try It

```bash
# Simple test
User: Use Codex to implement a sum function in src/utils/math.py

# More complex
User: Codex create a caching decorator in src/utils/cache.py
      Support TTL and LRU eviction
```

### Combine Workflows

```bash
# Full feature development
1. /superpowers:brainstorm - Design
2. /superpowers:write-plan - Plan tasks
3. codex-cli - Quick utilities
4. codex-subagent-driven-development - Main feature (TDD)
5. requesting-code-review - Final review
```

### Explore

- Try different task types (implement, fix, create, refactor)
- Experiment with file boundaries
- Combine with Gemini for analysis → Codex for implementation

---

## Resources

**Files:**
- Skill: `skills/codex-cli/SKILL.md`
- Agent: `agents/codex-executor.md`
- This guide: `docs/codex-cli-integration.md`

**Related:**
- Full TDD: `docs/quickstart-codex-subagent-workflow.md`
- Gemini integration: `docs/gemini-cli-integration.md`
- Superpowers: `README.md`

**Get Help:**
- GitHub: https://github.com/anna-belle-zhang/superpowerwithcodex/issues

---

**Ready for quick coding tasks? Say "Use Codex to..."** 🚀
