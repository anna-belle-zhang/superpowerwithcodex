---
name: codex-cli
description: Use when user requests Codex for one-off coding tasks (implement function, fix bug, create file) - dispatches to MCP codex-subagent for isolated execution, separate from full TDD workflow
---

# Codex CLI Integration

Dispatch Codex for quick coding tasks. For full TDD workflows, use codex-subagent-driven-development instead.

## When to Use

**Use for:** One-off implementations, quick fixes, file creation, refactoring
**Don't use for:** Full TDD workflows, test writing, code review, multi-step features

**Triggers:**
- "Use Codex to implement [function/feature]"
- "Let Codex write [code/file]"  
- "Codex create [file]"
- "Ask Codex to fix [issue]"

## Workflow

### 1. Recognize and Define
- Identify task (what to implement/fix)
- Define file boundaries (writable/read-only/off-limits)
- Extract requirements (signature, behavior, edge cases)

### 2. Dispatch
Use mcp__codex-subagent__spawn_agent with clear prompt containing boundaries and requirements.

### 3. Return Result
- Present changes (files created/modified, implementation details)
- Offer next steps (write tests, commit, modify)

## Examples

**Implement function:**
User: Use Codex to implement fibonacci in src/utils/math.py
Claude: *dispatches Codex*
Claude: Created fibonacci(n) in src/utils/math.py with recursion and memoization.
        Would you like me to write tests?

**Fix bug:**
User: Codex fix the off-by-one error in api/routes.py:45
Claude: *dispatches with boundary: modify api/routes.py only*
Claude: Fixed index calculation in routes.py:45. Changed `range(len(items))` to `range(len(items)+1)`.

**Create file:**
User: Let Codex create a logger utility in src/utils/logger.py
Claude: *dispatches Codex*  
Claude: Created logger.py with configurable log levels and file rotation.

## Best Practices

- Always define file boundaries
- Include verification method in prompt
- Offer to write tests after implementation
- Use codex-subagent-driven-development for full TDD workflow
