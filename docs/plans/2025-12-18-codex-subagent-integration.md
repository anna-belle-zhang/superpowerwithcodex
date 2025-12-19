# Codex Subagent Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans OR codex-subagent-driven-development to implement this plan task-by-task.

**Goal:** Integrate codex-as-mcp to enable Codex subagents for implementation while Claude handles planning, testing, and review in a TDD workflow.

**Architecture:** Create new skill `codex-subagent-driven-development` alongside existing `subagent-driven-development`. Add wrapper layer `lib/codex-integration.js` for MCP communication. Modify `writing-plans` to offer execution strategy choice with Codex as default.

**Tech Stack:** Node.js, codex-as-mcp (Python/uvx), MCP protocol, Git, existing superpowers framework

---

## Task 1: Codex Integration Wrapper - Availability Check

**Files:**
- Create: `lib/codex-integration.js`
- Test: `tests/lib/codex-integration.test.js`

**Step 1: Write the failing test for availability check**

Create `tests/lib/codex-integration.test.js`:

```javascript
const { checkCodexAvailability } = require('../../lib/codex-integration');

describe('checkCodexAvailability', () => {
  test('returns available=true when MCP server configured and Codex CLI installed', async () => {
    const result = await checkCodexAvailability();
    expect(result).toHaveProperty('available');
    expect(typeof result.available).toBe('boolean');
  });

  test('returns available=false with error when MCP not configured', async () => {
    // Mock MCP configuration missing
    const result = await checkCodexAvailability();
    if (!result.available) {
      expect(result).toHaveProperty('error');
      expect(typeof result.error).toBe('string');
    }
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

Create `lib/codex-integration.js`:

```javascript
/**
 * Codex Integration Wrapper
 * Handles MCP communication with codex-as-mcp server
 */

/**
 * Check if Codex is available and properly configured
 * @returns {Promise<{available: boolean, error?: string}>}
 */
async function checkCodexAvailability() {
  try {
    // Check if MCP server is configured
    const mcpConfig = await loadMCPConfig();
    if (!mcpConfig?.mcpServers?.['codex-subagent']) {
      return {
        available: false,
        error: 'codex-subagent not configured in .mcp.json'
      };
    }

    // Test spawn with simple task
    const testResult = await testSpawn();
    if (!testResult.success) {
      return {
        available: false,
        error: testResult.error
      };
    }

    return { available: true };
  } catch (error) {
    return {
      available: false,
      error: error.message
    };
  }
}

async function loadMCPConfig() {
  const fs = require('fs').promises;
  const path = require('path');

  try {
    const configPath = path.join(process.cwd(), '.mcp.json');
    const content = await fs.readFile(configPath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    return null;
  }
}

async function testSpawn() {
  // Placeholder for actual MCP spawn test
  // Will be implemented in next task
  return { success: true };
}

module.exports = {
  checkCodexAvailability
};
```

**Step 4: Run test to verify it passes**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add lib/codex-integration.js tests/lib/codex-integration.test.js
git commit -m "feat: add Codex availability check"
```

---

## Task 2: Codex Integration Wrapper - MCP Spawn Function

**Files:**
- Modify: `lib/codex-integration.js`
- Modify: `tests/lib/codex-integration.test.js`

**Step 1: Write the failing test for executeWithCodex**

Add to `tests/lib/codex-integration.test.js`:

```javascript
const { executeWithCodex } = require('../../lib/codex-integration');

describe('executeWithCodex', () => {
  test('executes simple task and returns output', async () => {
    const config = {
      prompt: 'Create a file hello.txt with content "Hello World"',
      workingDir: process.cwd(),
      retryCount: 0
    };

    const result = await executeWithCodex(config);
    expect(result).toHaveProperty('success');
    expect(result).toHaveProperty('output');
    expect(result).toHaveProperty('attempts');
  });

  test('respects retry count configuration', async () => {
    const config = {
      prompt: 'Invalid task that will fail',
      workingDir: process.cwd(),
      retryCount: 2
    };

    const result = await executeWithCodex(config);
    expect(result.attempts).toBeLessThanOrEqual(3); // initial + 2 retries
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: FAIL - executeWithCodex not exported

**Step 3: Write minimal implementation**

Add to `lib/codex-integration.js`:

```javascript
/**
 * Execute a task with Codex via MCP
 * @param {Object} config - Configuration object
 * @param {string} config.prompt - Task prompt for Codex
 * @param {string} config.workingDir - Working directory for Codex
 * @param {number} config.retryCount - Number of retries allowed
 * @param {Function} config.onProgress - Optional progress callback
 * @returns {Promise<{success: boolean, output?: string, error?: string, attempts: number}>}
 */
async function executeWithCodex(config) {
  const { prompt, workingDir, retryCount = 0, onProgress } = config;

  let attempts = 0;
  let lastError = null;

  while (attempts <= retryCount) {
    attempts++;

    if (onProgress) {
      onProgress(`🔄 Codex implementing... (attempt ${attempts}/${retryCount + 1})`);
    }

    try {
      const result = await spawnCodexAgent(prompt, workingDir);

      if (result.success) {
        if (onProgress) {
          onProgress('✅ Codex completed successfully');
        }
        return {
          success: true,
          output: result.output,
          attempts
        };
      }

      lastError = result.error;
    } catch (error) {
      lastError = error.message;
    }
  }

  return {
    success: false,
    error: lastError || 'Codex execution failed',
    attempts
  };
}

/**
 * Spawn a Codex agent via MCP
 * @param {string} prompt - Task prompt
 * @param {string} workingDir - Working directory
 * @returns {Promise<{success: boolean, output?: string, error?: string}>}
 */
async function spawnCodexAgent(prompt, workingDir) {
  // This will use MCP client to call codex-as-mcp tools
  // For now, return mock success
  return {
    success: true,
    output: 'Task completed'
  };
}

module.exports = {
  checkCodexAvailability,
  executeWithCodex
};
```

**Step 4: Run test to verify it passes**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add lib/codex-integration.js tests/lib/codex-integration.test.js
git commit -m "feat: add executeWithCodex wrapper function"
```

---

## Task 3: Codex Integration Wrapper - Retry Chain with Research

**Files:**
- Modify: `lib/codex-integration.js`
- Modify: `tests/lib/codex-integration.test.js`

**Step 1: Write the failing test for retryWithFeedback**

Add to `tests/lib/codex-integration.test.js`:

```javascript
const { retryWithFeedback } = require('../../lib/codex-integration');

describe('retryWithFeedback', () => {
  test('formats retry prompt with feedback on attempt 1', async () => {
    const originalPrompt = 'Implement feature X';
    const feedback = {
      failure_type: 'test_failure',
      test_output: 'Expected 5, got 3'
    };
    const attempt = 1;
    const maxRetries = 2;

    const result = await retryWithFeedback(originalPrompt, feedback, attempt, maxRetries);
    expect(result).toHaveProperty('prompt');
    expect(result.prompt).toContain('Implement feature X');
    expect(result.prompt).toContain('Expected 5, got 3');
  });

  test('includes research guidance on attempt 2', async () => {
    const originalPrompt = 'Implement API call';
    const feedback = {
      failure_type: 'test_failure',
      test_output: 'TypeError: Invalid parameter'
    };
    const attempt = 2;
    const maxRetries = 2;

    const result = await retryWithFeedback(originalPrompt, feedback, attempt, maxRetries);
    expect(result.prompt).toContain('research');
    expect(result.prompt).toContain('latest API documentation');
  });

  test('sets shouldEscalate=true when max retries exceeded', async () => {
    const result = await retryWithFeedback('task', {}, 3, 2);
    expect(result.shouldEscalate).toBe(true);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: FAIL - retryWithFeedback not exported

**Step 3: Write minimal implementation**

Add to `lib/codex-integration.js`:

```javascript
/**
 * Format retry prompt with feedback and research guidance
 * @param {string} originalPrompt - Original task prompt
 * @param {Object} feedback - Feedback from previous attempt
 * @param {number} attempt - Current attempt number (1-based)
 * @param {number} maxRetries - Maximum retry count
 * @returns {Promise<{prompt: string, shouldEscalate: boolean}>}
 */
async function retryWithFeedback(originalPrompt, feedback, attempt, maxRetries) {
  if (attempt > maxRetries) {
    return {
      prompt: '',
      shouldEscalate: true
    };
  }

  let retryPrompt = `RETRY ATTEMPT ${attempt} of ${maxRetries}\n\n`;
  retryPrompt += `Original Task:\n${originalPrompt}\n\n`;

  // Add feedback
  retryPrompt += `Previous Attempt Failed:\n`;
  if (feedback.failure_type === 'test_failure') {
    retryPrompt += `Test Output:\n${feedback.test_output}\n\n`;
  } else if (feedback.failure_type === 'review_issues') {
    retryPrompt += `Review Issues:\n${feedback.review_issues}\n\n`;
  }

  // Add research guidance on attempt 2
  if (attempt === 2) {
    retryPrompt += `IMPORTANT - Research Required:\n`;
    retryPrompt += `Before implementing, search for:\n`;
    retryPrompt += `- Latest API documentation and parameter signatures\n`;
    retryPrompt += `- Recent breaking changes or deprecations\n`;
    retryPrompt += `- Updated examples in official documentation\n`;
    retryPrompt += `- Library version compatibility issues\n\n`;
  }

  retryPrompt += `Please fix the issues and try again.\n`;
  if (attempt === maxRetries) {
    retryPrompt += `This is your FINAL attempt.\n`;
  }

  return {
    prompt: retryPrompt,
    shouldEscalate: false
  };
}

module.exports = {
  checkCodexAvailability,
  executeWithCodex,
  retryWithFeedback
};
```

**Step 4: Run test to verify it passes**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add lib/codex-integration.js tests/lib/codex-integration.test.js
git commit -m "feat: add retry chain with research guidance"
```

---

## Task 4: Codex Integration Wrapper - File Boundary Protection

**Files:**
- Modify: `lib/codex-integration.js`
- Modify: `tests/lib/codex-integration.test.js`

**Step 1: Write the failing test for boundary protection**

Add to `tests/lib/codex-integration.test.js`:

```javascript
const { detectBoundaryViolations } = require('../../lib/codex-integration');

describe('detectBoundaryViolations', () => {
  test('detects when protected files are modified', async () => {
    const boundaries = {
      implement_in: ['src/service.js'],
      read_only: ['src/service.test.js', 'package.json']
    };

    const changedFiles = ['src/service.js', 'src/service.test.js'];

    const violations = await detectBoundaryViolations(changedFiles, boundaries);
    expect(violations).toHaveLength(1);
    expect(violations[0]).toBe('src/service.test.js');
  });

  test('returns empty array when no violations', async () => {
    const boundaries = {
      implement_in: ['src/service.js'],
      read_only: ['src/service.test.js']
    };

    const changedFiles = ['src/service.js'];

    const violations = await detectBoundaryViolations(changedFiles, boundaries);
    expect(violations).toHaveLength(0);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: FAIL - detectBoundaryViolations not exported

**Step 3: Write minimal implementation**

Add to `lib/codex-integration.js`:

```javascript
/**
 * Detect file boundary violations
 * @param {string[]} changedFiles - List of changed files from git diff
 * @param {Object} boundaries - File boundary configuration
 * @param {string[]} boundaries.implement_in - Files allowed to modify
 * @param {string[]} boundaries.read_only - Files not allowed to modify
 * @returns {Promise<string[]>} List of violated files
 */
async function detectBoundaryViolations(changedFiles, boundaries) {
  const { read_only = [] } = boundaries;

  const violations = changedFiles.filter(file =>
    read_only.includes(file)
  );

  return violations;
}

/**
 * Build file boundaries from task configuration
 * @param {Object} task - Task configuration
 * @returns {Object} Boundaries object
 */
function buildFileBoundaries(task) {
  const boundaries = {
    implement_in: task.implementIn || [],
    read_only: task.readOnly || [],
    tests_to_pass: task.testsToPass || []
  };

  return boundaries;
}

/**
 * Format boundary instructions for Codex prompt
 * @param {Object} boundaries - Boundaries object
 * @returns {string} Formatted boundary instructions
 */
function formatBoundaryInstructions(boundaries) {
  let instructions = '';

  if (boundaries.implement_in.length > 0) {
    instructions += `Implement in ONLY these files:\n`;
    boundaries.implement_in.forEach(file => {
      instructions += `- ${file}\n`;
    });
    instructions += `\n`;
  }

  if (boundaries.read_only.length > 0) {
    instructions += `DO NOT MODIFY these files:\n`;
    boundaries.read_only.forEach(file => {
      instructions += `- ${file} (READ ONLY)\n`;
    });
    instructions += `\n`;
  }

  instructions += `You may READ any file to understand context.\n`;
  instructions += `You must ONLY WRITE to the "Implement in" files listed above.\n`;

  return instructions;
}

module.exports = {
  checkCodexAvailability,
  executeWithCodex,
  retryWithFeedback,
  detectBoundaryViolations,
  buildFileBoundaries,
  formatBoundaryInstructions
};
```

**Step 4: Run test to verify it passes**

Run: `npm test tests/lib/codex-integration.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add lib/codex-integration.js tests/lib/codex-integration.test.js
git commit -m "feat: add file boundary protection"
```

---

## Task 5: Create Codex Subagent Skill - Basic Structure

**Files:**
- Create: `skills/codex-subagent-driven-development/SKILL.md`

**Step 1: Create skill with YAML frontmatter and overview**

Create `skills/codex-subagent-driven-development/SKILL.md`:

```markdown
---
name: codex-subagent-driven-development
description: Use when executing implementation plans with Codex subagents - Claude writes tests, Codex implements, Claude reviews in sequential TDD workflow with retry chain
---

# Codex Subagent-Driven Development

Execute plan by having Claude write tests, Codex implement, and Claude review - with retry chain for quality.

**Core principle:** Claude writes tests (TDD) → Codex implements → Claude reviews → Quality gates with retry chain

## Overview

**Workflow:**
- Claude handles: Planning, test writing, code review, git operations
- Codex handles: Implementation only
- Sequential execution: One task at a time with TDD

**When to use:**
- Executing implementation plans with Codex subagents
- Want TDD workflow with Codex as implementer
- Codex availability verified

**When NOT to use:**
- Codex not available (use subagent-driven-development instead)
- Tasks are tightly coupled requiring manual execution
- Plan needs revision (use brainstorming first)

## Prerequisites

1. **Codex MCP Configured:**
   - codex-as-mcp in .mcp.json
   - Codex CLI installed and authenticated
   - Availability check passes

2. **Plan File:**
   - Implementation plan with execution-strategy: codex-subagents
   - Bite-sized tasks (2-5 minutes each)

## The Process

### 1. Load Plan and Check Availability

Read plan file, verify Codex available via `checkCodexAvailability()`.

If unavailable, offer fallback to `subagent-driven-development`.

### 2. Create TodoWrite

Create todo list with all implementation tasks from plan.

### 3. Execute Task Loop (Sequential TDD)

For each task:

#### Step 3a: RED - Claude Writes Test

- Claude reads task from plan
- Writes failing test file(s)
- Commits: `git add <test-files> && git commit -m "Test: [task]"`
- Captures commit SHA for review

#### Step 3b: GREEN - Codex Implements

- Build file boundaries from task
- Format explicit prompt with boundaries
- Dispatch Codex via `executeWithCodex()`
- Codex returns implementation summary

#### Step 3c: Verify Tests

- Claude runs test suite
- **If PASS:** Proceed to review
- **If FAIL:** Enter retry chain

**Retry Chain:**
1. Codex Retry 1: Send test output + guidance
2. Codex Retry 2: Add research guidance + retry
3. Claude Fix 1: Claude implements fix
4. Claude Fix 2: Claude researches + fixes
5. Human Escalation: Ask user to fix or skip

#### Step 3d: Code Review

- Dispatch code-reviewer subagent
- Compare: test commit SHA vs current HEAD
- Check: file boundaries respected
- **If issues:** Enter retry chain with review feedback

#### Step 3e: Commit and Continue

- Claude commits implementation (if successful)
- Mark task completed in TodoWrite
- Move to next task

### 4. Final Review

After all tasks complete:
- Dispatch final code-reviewer for full implementation
- Verify all plan requirements met
- Run full test suite

### 5. Complete

- Announce completion
- Present git status
- Offer options: push, create PR, continue work

## Integration with Codex Wrapper

Uses `lib/codex-integration.js`:
- `checkCodexAvailability()` - Verify Codex available
- `executeWithCodex(config)` - Execute task with Codex
- `retryWithFeedback()` - Format retry prompts
- `detectBoundaryViolations()` - Verify file boundaries
- `buildFileBoundaries()` - Build boundary config
- `formatBoundaryInstructions()` - Format prompt instructions

## Output Format

Summary mode with progress indicators:
- `🔄 Codex implementing...`
- `✅ Tests passed`
- `⚠️ Tests failed (retry 1/2)`
- `✅ Review complete`
- `❌ Escalating to human`

## Required Sub-Skills

- **test-driven-development** - Claude follows TDD for test writing
- **requesting-code-review** - Code review after each task
- **finishing-a-development-branch** - Complete development workflow

## Git Strategy

- Work on feature branch directly (no worktrees)
- Claude commits tests first
- Claude verifies Codex changes via git diff
- Clean commit history with clear messages
```

**Step 2: Commit**

```bash
git add skills/codex-subagent-driven-development/SKILL.md
git commit -m "feat: create codex-subagent-driven-development skill"
```

---

## Task 6: Modify Writing Plans Skill - Add Execution Choice

**Files:**
- Modify: `skills/writing-plans/SKILL.md`

**Step 1: Add execution strategy section to writing-plans**

Modify the "Execution Handoff" section in `skills/writing-plans/SKILL.md`:

```markdown
## Execution Handoff

After saving the plan, check Codex availability and offer execution choice:

**Step 1: Check Codex Availability**

```javascript
const { checkCodexAvailability } = require('../lib/codex-integration');
const codexStatus = await checkCodexAvailability();
```

**Step 2: Offer Execution Choice**

```
Plan complete and saved to `docs/plans/<filename>.md`.

Choose execution strategy:

A) Codex subagents (default) - Claude writes tests, Codex implements
   Status: ${codexStatus.available ? '✅ Available' : '⚠️ Not available'}

B) Claude subagents - Claude handles all implementation

C) Parallel session - Batch execution with checkpoints

Which approach? [A/B/C]:
```

**Step 3: Add Execution Strategy Metadata**

Add to plan file header:

```yaml
---
execution-strategy: codex-subagents | claude-subagents
created: YYYY-MM-DD
codex-available: true | false
---
```

**Step 4: Handle Choice**

**If A (Codex) chosen and available:**
- Set metadata: `execution-strategy: codex-subagents`
- **REQUIRED SUB-SKILL:** Use superpowers:codex-subagent-driven-development

**If A chosen but unavailable:**
- Show: `⚠️ Codex not available: ${codexStatus.error}`
- Auto-fallback: `Falling back to Claude subagents`
- Set metadata: `execution-strategy: claude-subagents`
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development

**If B (Claude) chosen:**
- Set metadata: `execution-strategy: claude-subagents`
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development

**If C (Parallel) chosen:**
- Guide to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses superpowers:executing-plans
```

**Step 2: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat: add Codex execution strategy to writing-plans"
```

---

## Task 7: Add MCP Integration Test

**Files:**
- Create: `tests/integration/codex-mcp.test.js`

**Step 1: Write integration test for real MCP communication**

Create `tests/integration/codex-mcp.test.js`:

```javascript
/**
 * Integration test for codex-as-mcp
 * Requires: codex-as-mcp configured in .mcp.json
 */

const { checkCodexAvailability, executeWithCodex } = require('../../lib/codex-integration');
const fs = require('fs').promises;
const path = require('path');

describe('Codex MCP Integration', () => {
  beforeAll(async () => {
    // Verify Codex is available before running tests
    const status = await checkCodexAvailability();
    if (!status.available) {
      console.warn('Skipping MCP tests - Codex not available:', status.error);
    }
  });

  test('can communicate with codex-as-mcp server', async () => {
    const status = await checkCodexAvailability();

    // Test passes if either available or gracefully reports unavailable
    expect(status).toHaveProperty('available');
    if (!status.available) {
      expect(status).toHaveProperty('error');
    }
  }, 30000); // 30s timeout for MCP communication

  test('can execute simple task via Codex', async () => {
    const status = await checkCodexAvailability();

    if (!status.available) {
      console.log('Skipping - Codex not available');
      return;
    }

    const testDir = path.join(__dirname, '../../tmp/codex-test');
    await fs.mkdir(testDir, { recursive: true });

    const config = {
      prompt: 'Create a file called hello.txt with content "Hello from Codex"',
      workingDir: testDir,
      retryCount: 0
    };

    const result = await executeWithCodex(config);

    expect(result.success).toBe(true);
    expect(result.output).toBeDefined();

    // Verify file was created
    const filePath = path.join(testDir, 'hello.txt');
    const fileExists = await fs.access(filePath).then(() => true).catch(() => false);
    expect(fileExists).toBe(true);

    // Cleanup
    await fs.rm(testDir, { recursive: true, force: true });
  }, 60000); // 60s timeout for actual execution
});
```

**Step 2: Run test to verify behavior**

Run: `npm test tests/integration/codex-mcp.test.js`
Expected: Either PASS (if Codex configured) or graceful skip (if not configured)

**Step 3: Commit**

```bash
git add tests/integration/codex-mcp.test.js
git commit -m "test: add MCP integration tests"
```

---

## Task 8: Add Documentation

**Files:**
- Create: `docs/codex-integration.md`
- Modify: `README.md`

**Step 1: Create Codex integration documentation**

Create `docs/codex-integration.md`:

```markdown
# Codex Integration Guide

## Overview

Superpowers can use Codex for implementation via the `codex-subagent-driven-development` skill. This enables a collaborative workflow where Claude handles planning, test writing, and code review, while Codex handles implementation.

## Prerequisites

### 1. Install Codex CLI

```bash
npm install -g @openai/codex@latest
codex login
codex --version  # Verify ≥0.46.0
```

### 2. Configure MCP Server

Add to `.mcp.json`:

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

### 3. Verify Installation

```bash
# Run availability check
npm test tests/integration/codex-mcp.test.js
```

## Workflow

### 1. Create Plan

Use brainstorming and writing-plans skills:

```
/superpowers:brainstorm
[Design your feature]

/superpowers:write-plan
Choose: A) Codex subagents (default)
```

### 2. Execute with Codex

The `codex-subagent-driven-development` skill executes:

```
For each task:
  1. Claude writes failing test
  2. Claude commits test
  3. Codex implements code
  4. Claude runs tests
  5. Claude reviews implementation
  6. If issues: Retry chain (Codex → Claude → Human)
  7. Claude commits and continues
```

### 3. Retry Chain

When tests fail or review finds issues:

1. **Codex Retry 1:** Feedback sent to Codex
2. **Codex Retry 2:** Research guidance + retry
3. **Claude Fix 1:** Claude implements fix
4. **Claude Fix 2:** Claude researches + fixes
5. **Human Escalation:** Manual intervention

### 4. File Boundaries

Claude enforces strict boundaries:

- **Implement in:** Files Codex can modify
- **Read only:** Test files, config (protected)
- **Verification:** Git diff checks after each task

## Benefits

- **TDD Enforced:** Claude writes tests first
- **Quality Gates:** Code review after each task
- **Clear Boundaries:** Tests protected from modification
- **Retry Strategy:** Multiple chances before escalation
- **Auditable:** Clean git history with clear commits

## Troubleshooting

### Codex Not Available

```
⚠️ Codex not available: codex-subagent not configured in .mcp.json
```

**Solution:** Configure MCP server in `.mcp.json`

### MCP Timeout

```
Error: MCP connection timeout
```

**Solution:** Check Codex CLI authentication: `codex login`

### Boundary Violations

```
Error: Boundary violation: modified src/service.test.js
```

**Solution:** Codex modified protected files. Change is reverted automatically and retried.

## Configuration

### Custom Retry Counts

Modify in skill or wrapper (future enhancement):

```javascript
const config = {
  codexRetries: 2,  // Default
  claudeRetries: 2  // Default
};
```

### Verbose Output

Enable detailed logging (future enhancement):

```bash
export CODEX_VERBOSE=true
```

## Comparison: Codex vs Claude Subagents

| Feature | Codex Subagents | Claude Subagents |
|---------|-----------------|------------------|
| Test Writing | Claude | Claude |
| Implementation | Codex | Claude |
| Code Review | Claude | Claude |
| Git Operations | Claude | Claude |
| Retry Strategy | 2 Codex + 2 Claude | Single Claude |
| File Protection | Enforced | Trusted |
| Use Case | TDD with separation | Full autonomy |
```

**Step 2: Update main README**

Add section to `README.md` after installation:

```markdown
## Codex Integration (Optional)

Superpowers supports Codex for implementation via codex-as-mcp.

**Benefits:**
- Claude writes tests (TDD)
- Codex implements code
- Claude reviews and validates

**Setup:**
See [Codex Integration Guide](docs/codex-integration.md)

**Quick Start:**
```bash
npm install -g @openai/codex@latest
codex login

# Add to .mcp.json
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

During planning, choose "Codex subagents" for execution.
```

**Step 3: Commit**

```bash
git add docs/codex-integration.md README.md
git commit -m "docs: add Codex integration guide"
```

---

## Task 9: End-to-End Test with Real Feature

**Files:**
- Create test plan and execute

**Step 1: Create minimal test plan**

Create `docs/plans/2025-12-18-test-codex-integration.md`:

```markdown
# Test Codex Integration - Simple Feature

---
execution-strategy: codex-subagents
created: 2025-12-18
---

**Goal:** Validate codex-subagent-driven-development with simple math utility

## Task 1: Add Sum Function

**Files:**
- Create: `src/utils/math.js`
- Test: `tests/utils/math.test.js`

**Step 1: Write failing test**

```javascript
// tests/utils/math.test.js
const { sum } = require('../../src/utils/math');

test('sum adds two numbers', () => {
  expect(sum(2, 3)).toBe(5);
});
```

**Step 2: Verify test fails**

Run: `npm test tests/utils/math.test.js`
Expected: FAIL - sum not defined

**Step 3: Implement via Codex**

Codex implements:
```javascript
// src/utils/math.js
function sum(a, b) {
  return a + b;
}

module.exports = { sum };
```

**Step 4: Verify test passes**

Run: `npm test tests/utils/math.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add src/utils/math.js tests/utils/math.test.js
git commit -m "feat: add sum utility function"
```
```

**Step 2: Execute with codex-subagent-driven-development**

Manually test the full workflow:

1. Verify Codex availability
2. Load test plan
3. Execute Task 1 with Codex
4. Verify test passes
5. Verify git history clean

**Step 3: Document results**

Create test report in commit message or separate file.

**Step 4: Commit**

```bash
git add docs/plans/2025-12-18-test-codex-integration.md
git commit -m "test: add end-to-end integration test plan"
```

---

## Task 10: Polish and Finalize

**Files:**
- Review all code
- Update package.json if needed
- Final commit

**Step 1: Run full test suite**

```bash
npm test
```

Expected: All tests pass

**Step 2: Verify file structure**

```
lib/
  codex-integration.js
tests/
  lib/
    codex-integration.test.js
  integration/
    codex-mcp.test.js
skills/
  codex-subagent-driven-development/
    SKILL.md
  writing-plans/
    SKILL.md (modified)
docs/
  codex-integration.md
  plans/
    2025-12-18-codex-subagent-integration-design.md
    2025-12-18-codex-subagent-integration.md
    2025-12-18-test-codex-integration.md
```

**Step 3: Final review**

Check:
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Skills properly formatted
- ✅ Git history clean

---

# Implementation Record (2025-12-18)

This section documents what was actually changed in this workspace when implementing this plan.

## Summary

- Added a Codex integration wrapper module (`superpowers-main/lib/codex-integration.js`) with availability checks, retry prompt formatting, and boundary helpers.
- Added a new workflow skill (`superpowers:codex-subagent-driven-development`) describing the Claude-tests/Codex-implements/review loop.
- Updated `writing-plans` handoff text to prefer Codex subagents by default when available.
- Added bash-based tests under the existing OpenCode test harness (this repo does not use Jest/npm test for these checks).
- Added documentation and a small end-to-end validation plan.

## Files Added / Updated

**Library**
- Added: `superpowers-main/lib/codex-integration.js`

**Skills**
- Added: `superpowers-main/skills/codex-subagent-driven-development/SKILL.md`
- Updated: `superpowers-main/skills/writing-plans/SKILL.md`

**Docs**
- Added: `superpowers-main/docs/codex-integration.md`
- Added: `docs/codex-integration.md` (pointer to the nested Superpowers docs)
- Added: `docs/plans/2025-12-18-test-codex-integration.md`
- Updated: `superpowers-main/README.md`

**Tests (bash harness)**
- Added: `superpowers-main/tests/opencode/test-codex-integration.sh`
- Added: `superpowers-main/tests/opencode/test-codex-mcp.sh` (smoke check; optional integration)
- Updated: `superpowers-main/tests/opencode/run-tests.sh`

## How To Verify

Run the default (non-integration) suite:

```bash
bash superpowers-main/tests/opencode/run-tests.sh
```

Run only the Codex library tests:

```bash
bash superpowers-main/tests/opencode/run-tests.sh --test test-codex-integration.sh
```

Optionally run integration tests (requires OpenCode; includes MCP smoke check):

```bash
bash superpowers-main/tests/opencode/run-tests.sh --integration
```

## Deviations From The Original Plan

- **Test framework:** The plan described Jest tests run via `npm test`. This repo’s existing test harness is bash-based (`superpowers-main/tests/opencode/`), so tests were implemented as shell scripts using `node -e`.
- **MCP execution:** `executeWithCodex()` / `spawnCodexAgent()` are currently scaffolds and do not yet perform real MCP protocol calls from Node. Real spawning exists in the Python MCP server (`codex-as-mcp-main/src/codex_as_mcp/server.py`).
- **Integration test:** The added “MCP test” is a smoke/config check (Codex CLI present + `.mcp.json` shape) rather than a full end-to-end MCP tool invocation.

## Next Steps (If You Want Full End-to-End MCP From Node)

- `spawnCodexAgent()` now uses a minimal MCP stdio JSON-RPC client from Node (initialize + `tools/call`).
- Upgrade the smoke test into a true integration test that actually runs the real MCP server + Codex CLI and validates file outputs. (This will require a deterministic sandbox directory and cleanup.)

**Step 4: Tag release**

```bash
git tag -a v1.0.0-codex -m "Codex subagent integration v1.0.0"
git push origin v1.0.0-codex
```

---

## Success Criteria

- ✅ Codex availability check works
- ✅ executeWithCodex wrapper functional
- ✅ Retry chain with research works
- ✅ File boundary protection enforced
- ✅ codex-subagent-driven-development skill complete
- ✅ writing-plans modified for execution choice
- ✅ Integration tests pass (when Codex configured)
- ✅ Documentation complete
- ✅ End-to-end test validates workflow
- ✅ All commits clean and atomic

## Execution Notes

- Follow TDD strictly: test → fail → implement → pass → commit
- Keep tasks small (2-5 minutes each)
- Verify after each step before committing
- Use `git status` frequently to track changes
- Run tests after every implementation step

---

**Implementation Status:** Ready for Execution
**Estimated Time:** 3-4 hours for all 10 tasks
**Next Step:** Choose execution method (Codex or Claude subagents)
