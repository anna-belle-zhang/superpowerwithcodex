# Codex Subagent Integration Design

**Date:** 2025-12-18
**Status:** Design Complete - Ready for Implementation
**Goal:** Integrate codex-as-mcp to enable Codex subagents for implementation while Claude handles planning, testing, and review

---

## 1. System Overview & Workflow

### Integration Goal
Enable superpowers to use Codex for implementation while Claude handles planning, testing, and review in a test-driven development workflow.

### Prerequisites & Setup

**1. Codex CLI Installation:**
- Install: `npm install -g @openai/codex@latest` (requires ≥0.46.0)
- Authenticate: `codex login`
- Verify: `codex --version`

**2. MCP Server Configuration:**

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

**3. Availability Test:**
- During planning phase, verify MCP connection
- Test spawn: Simple "create hello.txt" task
- Confirm Codex responds and completes task

### Core Architecture

- **New Skill:** `codex-subagent-driven-development` (parallel to existing `subagent-driven-development`)
- **Wrapper Layer:** `lib/codex-integration.js` (handles MCP communication, retry logic)
- **Modified Planning:** `writing-plans` skill extended to offer execution strategy choice
- **Git Strategy:** Direct feature branch work (no worktrees when using Codex)

### Task Execution Flow

1. **Planning Phase:** User creates plan via `writing-plans`, chooses "Codex subagents" execution (default)
2. **Availability Check:** Verify codex-as-mcp configured, Codex CLI authenticated
3. **Per-Task Loop (Sequential):**
   - Claude writes test file → commits to git
   - Claude dispatches Codex with explicit file boundaries
   - Codex implements → Claude runs tests
   - **Retry Chain:** Codex (2 attempts) → Claude fix (2 attempts) → Human escalation
   - Claude reviews implementation
   - If review issues: same retry chain
   - Mark complete, next task
4. **Completion:** Claude does final review and git operations

---

## 2. Task Execution Cycle (TDD Loop)

### Sequential Per-Task Workflow

**Step 1: Test Creation (Claude)**
- Claude reads task from plan
- Writes test file(s) following TDD principles (RED phase)
- Commits tests: `git add <test-files> && git commit -m "Test: [task description]"`
- Captures commit SHA for review comparison

**Step 2: Implementation Dispatch (Codex via MCP)**

Claude constructs explicit prompt:
```
Implement Task N: [description]

Tests to pass: [test file paths]
Implement in: [implementation file paths]
DO NOT MODIFY: [test files, other protected files]

Run tests with: [test command]
All tests must pass.
```

- Wrapper calls `spawn_agent(prompt)`
- Codex works in current directory (feature branch)
- Returns: Implementation summary + test results

**Step 3: Test Verification (Claude)**
- Claude runs test suite
- **If PASS:** Proceed to review (Step 4)
- **If FAIL:** Enter retry chain:
  - **Codex Retry 1-2:** Send test output + guidance to Codex
  - **Claude Fix 1-2:** If Codex exhausts retries, Claude fixes
  - **Human Escalation:** If both fail, stop and ask human

**Step 4: Code Review (Claude)**
- Use existing `code-reviewer` agent
- Compare: committed tests vs new implementation
- Check: file boundaries respected, no test modifications
- If issues: enter retry chain with review feedback

---

## 3. Wrapper Layer (`lib/codex-integration.js`)

### Module Responsibilities
- Abstract MCP tool calls (`spawn_agent`, `spawn_agents_parallel`)
- Handle retry logic and error formatting
- Provide clean interface for skills to use

### Core Functions

```javascript
// Main execution function
async function executeWithCodex(config) {
  // config: { prompt, workingDir, retryCount, onProgress }
  // Returns: { success, output, error, attempts }
}

// Availability check
async function checkCodexAvailability() {
  // Verify: MCP server configured, Codex CLI installed
  // Test: Simple spawn to confirm working
  // Returns: { available: boolean, error?: string }
}

// Retry chain handler
async function retryWithFeedback(prompt, feedback, attempt, maxRetries) {
  // Formats: test failures, review feedback
  // Tracks: attempt number, previous outputs
  // Returns: { success, output, shouldEscalate }
}
```

### Output Formatting

**Summary mode (default):**
- Emit progress events:
  - `"🔄 Codex implementing..."`
  - `"✅ Tests passed"` / `"⚠️ Tests failed (retry 1/2)"`
  - `"✅ Review complete"`
- Capture full logs for verbose mode (future enhancement)

### Error Handling
- MCP connection failures → graceful error, suggest config check
- Codex CLI errors → capture stderr, surface to Claude
- Timeout handling → configurable timeout per spawn

---

## 4. Skill Implementation (`codex-subagent-driven-development`)

### File Location
`skills/codex-subagent-driven-development/SKILL.md`

### YAML Frontmatter
```yaml
---
name: codex-subagent-driven-development
description: Use when executing implementation plans with Codex subagents - Claude writes tests, Codex implements, Claude reviews in sequential TDD workflow with retry chain
---
```

### Skill Structure

**1. Prerequisites Check**
- Verify plan file exists
- Check Codex availability via wrapper
- If unavailable: offer fallback to regular `subagent-driven-development`

**2. TodoWrite Setup**
- Load plan tasks
- Create todo list with all implementation tasks

**3. Task Loop**

For each task:
- **RED:** Claude writes failing test, commits
- **GREEN:** Dispatch Codex with file boundaries
- **Verify:** Run tests, handle retry chain
- **Review:** Code review with git diff
- **Commit:** Claude commits implementation (or retry/escalate)
- Mark complete, next task

**4. Final Review & Completion**
- Dispatch final code-reviewer for full implementation
- Verify all plan requirements met
- Present completion options (no worktree cleanup needed)

### Integration Points
- Import: `lib/codex-integration.js` for MCP calls
- Reuse: `agents/code-reviewer.md` for reviews
- Follow: TDD principles from `test-driven-development` skill

---

## 5. Planning Phase Integration

### Modify
`skills/writing-plans/SKILL.md` (or create hook in planning workflow)

### Execution Strategy Selection

After plan is written and validated, before saving to file:

```
Planning complete! Choose execution strategy:

A) Codex subagents (default) - Claude writes tests, Codex implements
B) Claude subagents - Claude handles all implementation

Which execution method? [A/B]:
```

### If User Chooses A (Codex - Default)

**1. Availability Check:**
```javascript
const { available, error } = await checkCodexAvailability();
```

**2. If Available:**
- Add metadata to plan:
  ```yaml
  ---
  execution-strategy: codex-subagents
  created: YYYY-MM-DD
  ---
  ```
- Confirm: `"✅ Codex available. Using codex-subagent-driven-development"`

**3. If Unavailable:**
- Show warning: `"⚠️ Codex not available: {error}"`
- Auto-fallback: `"Falling back to Claude subagents"`
- Update metadata: `execution-strategy: claude-subagents`

### If User Explicitly Chooses B (Claude)
- No availability check needed
- Set metadata: `execution-strategy: claude-subagents`

### Backward Compatibility
- Plans without metadata check Codex availability, fallback to Claude if needed

---

## 6. Retry Chain Logic & Error Handling

### Retry Chain Flow

```
Test/Review Failure
    ↓
Codex Attempt 1 (with feedback)
    ↓ (if still fails)
Codex Attempt 2 (with feedback + SEARCH for latest info)
    ↓ (if still fails)
Claude Fix Attempt 1 (direct fix)
    ↓ (if still fails)
Claude Fix Attempt 2 (with SEARCH + fix)
    ↓ (if still fails)
Human Escalation
```

### Codex Retry Format

```javascript
// Retry prompt structure
{
  original_task: "[task description]",
  previous_attempt: "[Codex's implementation summary]",
  failure_type: "test_failure" | "review_issues",
  feedback: {
    test_output: "[test failure messages]",
    // OR
    review_issues: "[Critical/Important issues from code-reviewer]"
  },
  guidance: "[Claude's interpretation: what went wrong, what to fix]",
  attempt: "1 of 2" | "2 of 2 (FINAL)"
}
```

### Second Attempt Enhancement

For **Codex Attempt 2** and **Claude Fix Attempt 2**, add research step:

```javascript
{
  attempt: "2 of 2 (FINAL)",
  research_required: true,
  search_guidance: [
    "Check latest API documentation for: [identified dependencies]",
    "Verify library versions and parameter signatures",
    "Search for recent breaking changes or deprecations",
    "Look for updated examples in official docs"
  ],
  tools_available: [
    "WebSearch", // for Claude
    "Documentation lookup" // for Codex if available
  ]
}
```

### Research Targets
- API parameter names/types (common cause of failures)
- Library version compatibility
- Framework-specific patterns
- Recent deprecations or breaking changes

### Implementation
- **Codex:** Include research instructions in prompt, Codex can use its own search
- **Claude:** Uses WebSearch or Context7 MCP, updates understanding before fix

### Claude Fix Strategy
- Claude analyzes: Codex's attempts + all feedback
- Identifies: Pattern in failures (misunderstood requirement, technical limitation)
- Fixes: Directly implements solution
- Commits: Separate commit noting "Fixed after Codex retry exhaustion"

### Human Escalation

Triggered when both Codex and Claude exhaust retries.

**Presents:**
- Task description
- All attempt summaries
- All feedback/test failures
- Current code state (git diff)

**Options:**
- Fix manually
- Skip task
- Abort plan
- Switch to Claude-only mode

---

## 7. File Boundaries & Git Protection

### Protection Strategy
Explicit Lists + Git Verification

### Step 1: Claude Defines Boundaries (Before Codex Dispatch)

```javascript
// Build file lists from task
const boundaries = {
  implement_in: [
    "src/user-service.ts",
    "src/types/user.ts"
  ],
  read_only: [
    "src/user-service.test.ts", // tests Claude wrote
    "src/config.ts",            // shared config
    "package.json"              // dependencies
  ],
  tests_to_pass: [
    "src/user-service.test.ts"
  ]
};
```

### Step 2: Explicit Prompt to Codex

```markdown
Implement in ONLY these files:
- src/user-service.ts
- src/types/user.ts

DO NOT MODIFY these files:
- src/user-service.test.ts (tests - READ ONLY)
- src/config.ts (shared config)
- package.json (dependencies)

You may READ any file to understand context.
You must ONLY WRITE to the "Implement in" files listed above.
```

### Step 3: Git-Based Verification

```javascript
// After Codex completes
const beforeSHA = /* SHA when tests were committed */;
const afterSHA = /* current HEAD */;

// Check what changed
const changedFiles = await gitDiff(beforeSHA, afterSHA);

// Verify boundaries
const violations = changedFiles.filter(f =>
  boundaries.read_only.includes(f)
);

if (violations.length > 0) {
  // CRITICAL violation - Codex modified protected files
  return {
    success: false,
    error: `Boundary violation: modified ${violations.join(', ')}`,
    action: "revert_and_retry"
  };
}
```

### Step 4: Violation Handling
- Revert: `git reset --hard {beforeSHA}`
- Log violation for debugging
- Retry with stronger boundary emphasis
- Counts toward retry limit

---

## 8. Testing & Validation Strategy

### Following Superpowers TDD Methodology

### Phase 1: Pressure Testing (RED)

Create test scenarios WITHOUT the skill to establish baseline:

**1. Codex Availability Test:**
- Scenario: MCP not configured
- Expected: Graceful error, fallback offered

**2. Boundary Violation Test:**
- Scenario: Give Codex vague boundaries
- Expected: May modify test files (baseline behavior)

**3. Retry Chain Test:**
- Scenario: Implementation fails tests
- Expected: Without skill, no retry structure

### Phase 2: Skill Implementation (GREEN)

Build skill to address baseline failures:

**1. Unit Tests for Wrapper (`lib/codex-integration.js`):**
```javascript
test('checkCodexAvailability returns false when MCP not configured')
test('executeWithCodex respects retry limits')
test('retryWithFeedback formats research guidance on attempt 2')
test('detectBoundaryViolations identifies modified test files')
```

**2. Integration Tests (Simple Task):**
- Create minimal plan: "Add function to sum two numbers"
- Claude writes test
- Verify Codex receives correct prompt with boundaries
- Verify implementation passes tests
- Verify git commits are clean

**3. Retry Chain Test:**
- Create intentionally ambiguous task
- Force test failure
- Verify: Codex retry → Claude fix → escalation flow

### Phase 3: Real-World Validation

Test with actual superpowers development:
- Pick simple feature from backlog
- Run full codex-subagent-driven-development workflow
- Verify: planning, execution, review, completion
- Document: successes, failures, edge cases

### Success Criteria
- ✅ Codex availability check works
- ✅ File boundaries enforced (0 violations)
- ✅ Retry chain executes correctly
- ✅ Falls back to Claude when Codex unavailable
- ✅ Git history clean and auditable

---

## 9. Edge Cases, Limitations & Future Enhancements

### Known Limitations

**1. No Parallel Execution (Initial Version):**
- Sequential only for TDD workflow
- Future: Support `spawn_agents_parallel` for independent tasks
- Requires: Careful git merge handling

**2. Codex Context Limits:**
- Large codebases may exceed Codex context
- Mitigation: Keep tasks small (2-5 minutes as per superpowers)
- Future: Context summarization in prompts

**3. Platform-Specific Commands:**
- Test commands vary by project (npm test, pytest, etc.)
- Solution: Detect from package.json or plan metadata
- Fallback: Ask during planning phase

### Edge Cases

**1. Network Failures During Codex Spawn:**
- MCP timeout or connection loss
- Handling: Retry MCP call (separate from implementation retries)
- Max: 2 MCP connection retries before escalation

**2. Codex Modifies Unexpected Files:**
- Creates new files not in boundaries
- Handling: Git diff catches this, treat as boundary violation
- Action: Revert and retry with explicit "only modify existing files" if needed

**3. Test Command Fails (Not Code Issue):**
- Missing dependencies, environment issues
- Detection: Same failure across all retries without code changes
- Handling: Escalate to human with environment diagnosis

### Future Enhancements

**1. Parallel Task Support:** Use `spawn_agents_parallel` for independent tasks

**2. Metrics Dashboard:** Track success rates, retry counts, Codex vs Claude performance

**3. Learning Mode:** Analyze failure patterns, improve prompts over time

**4. Custom Retry Strategies:** Per-project configuration for retry counts and escalation

---

## Implementation Roadmap

### Phase 1: Core Infrastructure
1. Implement `lib/codex-integration.js` wrapper
2. Add Codex availability check
3. Test MCP integration end-to-end

### Phase 2: Skill Development
1. Create `codex-subagent-driven-development` skill
2. Implement retry chain logic with research enhancement
3. Add file boundary protection

### Phase 3: Planning Integration
1. Modify `writing-plans` to offer execution choice
2. Set Codex as default with fallback
3. Add plan metadata support

### Phase 4: Testing & Validation
1. Unit tests for wrapper layer
2. Integration tests with simple tasks
3. Real-world validation with superpowers features

### Phase 5: Documentation & Polish
1. Update README with Codex integration docs
2. Create troubleshooting guide
3. Add examples and best practices

---

## Success Metrics

- **Availability:** 95%+ Codex availability check accuracy
- **Boundaries:** 0% boundary violations in production use
- **Retry Efficiency:** <30% tasks require Claude fix (most resolved by Codex retry)
- **Human Escalation:** <10% tasks escalate to human
- **Test Coverage:** 100% of wrapper layer functions tested
- **User Adoption:** Codex becomes default execution choice

---

**Design Status:** ✅ Complete and Validated
**Next Step:** Create implementation plan using `writing-plans` skill
