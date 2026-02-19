---
name: ralph-codex-e2e
description: Use when executing plans with Ralph Wiggum loop - Codex handles dev + unit + integration tests, Claude handles E2E tests, loops until all tests green
---

# Ralph-Codex-E2E Workflow

Execute a plan using Ralph Wiggum's persistent loop with Codex for implementation/unit/integration tests and Claude for E2E tests.

**Core principle:** Ralph loops → Codex (dev + unit + integ) → Claude (E2E) → all green = done

## Overview

**Agent responsibilities:**
- **Ralph Wiggum:** Outer loop via Stop hook, continues until completion
- **Codex:** Implementation + unit tests + integration tests (network enabled)
- **Claude:** E2E tests only (project-specific auto-detection)

**When to use:**
- You want autonomous execution until all tests pass
- Project has unit, integration, AND E2E test requirements
- You can walk away and let it run

**When NOT to use:**
- Need human review between tasks (use `codex-subagent-driven-development`)
- No E2E tests needed (use `codex-subagent-driven-development`)
- Codex unavailable (use `subagent-driven-development`)

## Prerequisites

### 1. Codex Network Configuration

Codex needs network access for integration tests. Create `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

**Important:**
- Path: `~/.codex/` (NOT `~/.config/codex/`)
- Section: `[sandbox_workspace_write]` (underscores, NOT dots)
- Restart Claude Code after config changes

Verify: `codex e --full-auto "curl -s https://api.github.com/zen"`

### 1b. Azure CLI (if needed)

For Azure integration tests, install native Linux CLI:

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Azure credentials workaround:
```bash
export AZURE_CONFIG_DIR=/tmp/azure
cp -r ~/.azure /tmp/azure
```

### 2. Ralph Wiggum Plugin

```bash
/plugin install ralph-wiggum@claude-plugins-official
```

### 3. Codex MCP Configuration

`.mcp.json` must contain:

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

### 4. A Written Plan

- Saved under `docs/plans/YYYY-MM-DD-<feature>.md`
- Tasks are small (2-5 minutes each)
- Clear test requirements per task

## The Process

### 1. Start Ralph Loop

Construct the Ralph prompt with the plan:

```bash
/ralph-loop "Execute plan: docs/plans/YYYY-MM-DD-feature.md
Specs directory: docs/specs/<feature>/ (if exists, read delta specs for scenarios)

For each task in the plan:

CODEX PHASE:
1. Read the task requirements
2. If specs exist, read the delta specs — each GIVEN/WHEN/THEN scenario is a contractual requirement
3. Implement the feature code
4. Write unit tests for the implementation (derive from scenarios when available)
5. Write integration tests (if task requires external calls)
6. Run unit tests - must pass
7. Run integration tests - must pass

CLAUDE PHASE:
8. Detect project type for E2E strategy
9. Run E2E tests appropriate to project
10. Commit if all tests green

COMPLETION:
- All tasks done with all tests passing = output DONE
- Any test fails = fix and retry

Loop until ALL tests green for ALL tasks, then output: DONE
" --max-iterations 50 --completion-promise "DONE"
```

### 2. Codex Phase (Per Task)

Codex handles implementation and lower-level tests:

**Implementation:**
- Read task from plan
- Write implementation code
- Stay within file boundaries (if specified)

**Unit Tests:**
- Write unit tests covering the implementation
- Run unit tests
- If fail → Codex retries with feedback (2x max)

**Integration Tests:**
- Write integration tests for external dependencies
- Run integration tests (network enabled via config)
- If fail → Codex retries with feedback (2x max)

### 3. Claude Phase (Per Task)

Claude handles E2E tests after Codex completes:

**Project Type Detection:**

| Detection | E2E Strategy |
|-----------|--------------|
| `playwright.config.*` exists | Playwright browser tests |
| `cypress.config.*` exists | Cypress browser tests |
| `package.json` has web framework | Playwright browser tests |
| OpenAPI/Swagger spec exists | API E2E via curl/httpie |
| CLI tool (bin in package.json) | Bash-based CLI tests |
| Default | Bash system tests |

**E2E Execution:**
- Run E2E tests appropriate to detected type
- If fail → Claude retries (2x max)
- If still fails → Ralph loops with same prompt

### 4. Retry Chain

| Stage | Agent | Max Retries | On Exhaust |
|-------|-------|-------------|------------|
| Unit test fail | Codex | 2 | Claude fix (2x) |
| Integration test fail | Codex | 2 | Claude fix (2x) |
| E2E test fail | Claude | 2 | Ralph loops |
| All retries exhausted | - | - | Human escalation |

**Retry with feedback format:**

```
RETRY ATTEMPT N of 2

Original task: [task description]

Previous attempt failed:
[test output / error messages]

Guidance:
- [specific issue identified]
- [suggested fix approach]

Please fix and try again.
```

### 5. Completion

Ralph exits loop when:
- All tasks completed
- All unit tests passing
- All integration tests passing
- All E2E tests passing
- "DONE" output triggered

### 6. Post-Loop Verification and Archiving

After Ralph exits:
- Review git history for all commits
- Run full test suite one final time
- **If `docs/specs/<feature>/` exists:**
  - Use `superpowers:verify-specs` to verify all scenarios are covered
  - If verification passes: use `superpowers:archive-specs` to merge deltas into living specs
  - If verification fails: fix missing coverage before proceeding
- Use `superpowers:finishing-a-development-branch` if needed

## E2E Detection Logic

```javascript
function detectE2EStrategy(projectRoot) {
  // Browser-based E2E
  if (exists('playwright.config.ts') || exists('playwright.config.js')) {
    return { type: 'playwright', command: 'npx playwright test' };
  }
  if (exists('cypress.config.ts') || exists('cypress.config.js')) {
    return { type: 'cypress', command: 'npx cypress run' };
  }

  // Check package.json for web frameworks
  const pkg = readPackageJson();
  if (pkg.dependencies?.react || pkg.dependencies?.vue || pkg.dependencies?.angular) {
    return { type: 'playwright', command: 'npx playwright test' };
  }

  // API E2E
  if (exists('openapi.yaml') || exists('swagger.json')) {
    return { type: 'api', command: 'npm run test:e2e' };
  }

  // CLI E2E
  if (pkg.bin) {
    return { type: 'cli', command: 'npm run test:e2e' };
  }

  // Default: bash-based
  return { type: 'bash', command: 'npm run test:e2e || ./test/e2e.sh' };
}
```

## Example Workflow

```
User: /ralph-loop "Execute plan: docs/plans/2026-01-25-auth-feature.md ..."

Ralph Loop Iteration 1:
├─ Task 1: User login endpoint
│  ├─ CODEX: Implements POST /login
│  ├─ CODEX: Writes unit tests (5 tests)
│  ├─ CODEX: Writes integration tests (2 tests)
│  ├─ CODEX: Runs tests → 7/7 pass ✅
│  ├─ CLAUDE: Detects API project
│  ├─ CLAUDE: Runs E2E curl tests → pass ✅
│  └─ Commit: "Feat: User login endpoint"
│
├─ Task 2: JWT token validation
│  ├─ CODEX: Implements middleware
│  ├─ CODEX: Unit tests → 3/4 fail ❌
│  ├─ CODEX: Retry 1 with feedback → 4/4 pass ✅
│  ├─ CODEX: Integration tests → pass ✅
│  ├─ CLAUDE: E2E → pass ✅
│  └─ Commit: "Feat: JWT validation middleware"
│
└─ All tasks complete, all tests green
   └─ Output: DONE

Ralph exits loop. ✅
```

## Red Flags

**Never:**
- Skip E2E phase (defeats the purpose of this workflow)
- Disable Codex network (integration tests will fail)
- Set --max-iterations too low (complex features need room)
- Use for tasks without clear test requirements

**If stuck in loop:**
- Check if task requirements are ambiguous
- Verify Codex network is enabled
- Check E2E detection is correct for project
- Consider human intervention via `/cancel-ralph`

## Integration

**Required plugins:**
- `ralph-wiggum@claude-plugins-official`

**Required MCP:**
- `codex-subagent` (codex-as-mcp)

**Related skills:**
- `superpowers:codex-subagent-driven-development` - Without Ralph loop
- `superpowers:subagent-driven-development` - Claude-only (no Codex)
- `superpowers:finishing-a-development-branch` - Post-completion cleanup

**Configuration:**
- Codex network: `~/.config/codex/config.toml`
- See: `docs/codexintetest.md` for troubleshooting
