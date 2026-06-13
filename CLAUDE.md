# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

don't ask permission for low risk actions

## Project Overview

Superpowers is a complete software development workflow system for coding agents, built on composable "skills" that enforce systematic processes. It transforms how agents approach development by requiring design before code, comprehensive planning before implementation, and test-driven development throughout.

This repository is a **fork of [obra/superpowers](https://github.com/obra/superpowers)** that adds Codex integration: Claude writes specs and E2E tests, Codex implements code and writes unit/integration tests.

**Core Philosophy:**
- Test-Driven Development (write tests first, always)
- Systematic over ad-hoc (process over guessing)
- Complexity reduction (simplicity as primary goal)
- Evidence over claims (verify before declaring success)

## Running Tests

**Python tests** (pytest configured via `pytest.ini`, testpaths = `tests/`):
```bash
pytest                                          # All Python tests
pytest tests/structured-specs-integration/     # One suite
pytest tests/structured-specs-integration/test_commands.py::test_name  # Single test
```

The `tests/structured-specs-integration/` suite validates this repo's own conventions — skill files, command files, CLAUDE.md content, spec directory structure. Run it after editing skills, commands, or this file.

**Shell-based suites:**
```bash
bash tests/opencode/run-tests.sh               # OpenCode plugin tests (--integration for full run)
bash tests/e2e/ralph-codex-e2e/run-tests.sh    # E2E scenarios (requires codex CLI + ~/.codex/config.toml)
```

**JS tests** (`tests/lib/*.test.js`): Jest ESM tests for `lib/codex-integration.js` and `lib/ralph-orchestrator.js`. There is no root `package.json`; jest must be available and run with `NODE_OPTIONS=--experimental-vm-modules` (they use `jest.unstable_mockModule`).

Note: `src/` and the top-level test files (`tests/test_jwt_auth.py`, etc.) are sample code produced by spec-driven workflow runs, not the plugin itself.

## Architecture

### Skills System

**Skill Structure:**
```
skills/
  skill-name/
    SKILL.md              # Main reference (YAML frontmatter + markdown)
    supporting-file.*     # Only if needed for tools/heavy reference
```

**Skill Discovery:**
- Skills use YAML frontmatter: `name` and `description` fields (max 1024 chars total)
- Description starts with "Use when..." for search optimization
- Skills auto-activate based on context matching
- Personal skills (~/.claude/skills) can shadow superpowers skills

**Core Utility:** `lib/skills-core.js`
- `extractFrontmatter()` - Parse YAML from SKILL.md files
- `findSkillsInDir()` - Recursively discover skills with namespacing
- `resolveSkillPath()` - Handle skill shadowing (personal overrides superpowers)
- `stripFrontmatter()` - Extract content without YAML

### Plugin System

**Configuration:**
- `.claude-plugin/plugin.json` - Plugin metadata
- `.claude-plugin/marketplace.json` - Marketplace configuration
- `hooks/hooks.json` - SessionStart hook (injects using-superpowers skill) and UserPromptSubmit hook (injects mandatory workflow rules every turn)

**Commands:**
- `/superpowerwithcodex:brainstorm` - Interactive design refinement
- `/superpowerwithcodex:write-plan` - Create implementation plan
- `/superpowerwithcodex:execute-plan` - Execute plan in batches
- `/superpowerwithcodex:write-specs` - Create structured specifications with testable scenarios
- `/superpowerwithcodex:verify-specs` - Verify all spec scenarios have corresponding tests
- `/superpowerwithcodex:archive-specs` - Archive delta specs into living specifications
- `/superpowerwithcodex:search` - Search remote marketplace catalog for skills by keyword

### Codex Integration Layer

Two JS modules in `lib/` implement the Claude↔Codex orchestration:

- `lib/codex-integration.js` - Codex availability checks, MCP config loading (`.mcp.json`), task dispatch (`executeWithCodex`), retry with feedback, and E2E strategy detection (`detectE2EStrategy` sniffs for Playwright/Cypress/etc.)
- `lib/ralph-orchestrator.js` - Ralph-Codex-E2E loop: Codex handles implementation + unit + integration tests, Claude runs E2E tests, loop until green

Codex runs sandboxed; implementation tasks require `workspace-write` mode and `network_access = true` in `~/.codex/config.toml` (see README "Codex Permissions").

### Directory Structure

- `skills/` - All skill definitions (flat namespace)
- `commands/` - Slash command definitions
- `agents/` - Agent definitions (e.g., code-reviewer)
- `lib/` - Core utilities (skills-core.js, codex-integration.js, ralph-orchestrator.js)
- `hooks/` - Lifecycle hooks
- `docs/plans/` - Design docs (`YYYY-MM-DD-<topic>-design.md`)
- `docs/specs/` - Structured specs (see Structured Specifications below)
- `tests/` - Python, JS, and shell test suites
- `repos/` - Vendored reference repositories (not part of the plugin)
- `src/` - Sample output from spec-driven workflow runs (not plugin code)

## Development Workflow

### The Superpowers Cycle

1. **brainstorming** - Before writing code, refine ideas through questions, explore alternatives, present design in sections. After understanding the purpose, dispatch a research subagent (Codex by default) to survey best practices and available repos — research is low-risk, no permission needed. Saves to `docs/plans/YYYY-MM-DD-<topic>-design.md`

2. **writing-specs** *(optional)* - Transform brainstorm output into structured specs with GIVEN/WHEN/THEN scenarios. Creates `docs/specs/<feature>/` with proposal, design, and delta specs

3. **using-git-worktrees** - After design approval, ask user permist to create isolated workspace on new branch, verify clean test baseline

4. **writing-plans** - Break work into 2-5 minute tasks with exact file paths, complete code, verification steps. When specs exist, tasks include scenario tables

5. **subagent-driven-development** or **executing-plans** - Dispatch fresh subagent per task or execute in batches with checkpoints. When specs exist, scenarios become inviolable contracts

6. **test-driven-development** - Enforces RED-GREEN-REFACTOR cycle. Write failing test, watch it fail, write minimal code, watch it pass

7. **requesting-code-review** - Review against plan between tasks, block progress on critical issues

8. **verifying-specs** *(when specs exist)* - Verify completeness, correctness, and coherence of specs against implementation

9. **finishing-a-development-branch** - Verify tests (and specs if they exist), present merge/PR options, cleanup

10. **archiving-specs** *(when specs exist)* - Merge delta specs into living specs, archive feature directory

**CRITICAL: These workflows are mandatory, not suggestions. Skills are enforced processes.**

### Codex Workflows (this fork)

**Specs-first (recommended)** — `claude-codex-specs-tdd` + `spec-driven-tdd`:
Claude writes GIVEN/WHEN/THEN specs, dispatches Codex with only the spec path. Codex derives its own plan and tests, implements, and writes `progress.md` into the spec folder for re-entry. Claude runs E2E tests and verifies specs after Codex returns. In this workflow **Claude never writes unit/integration tests** — Codex derives them from the specs.

Dispatch format:
```
Use superpowerwithcodex:spec-driven-tdd
Spec directory: docs/specs/<feature>/
Implement in: src/
Tests in: tests/
Test command: <test command>
```

**Tests-first** — `codex-subagent-driven-development`: Claude writes tests (RED), Codex implements (GREEN), Claude reviews (REFACTOR), with file-boundary protection and a retry chain.

**Ralph loop** — `ralph-codex-e2e`: Codex handles dev + unit + integration tests, Claude handles E2E, loops until all green.

**One-off tasks** — `codex-cli` skill dispatches via the `codex:codex-rescue` subagent.

## Working with Skills

### Creating New Skills

**MUST follow TDD for skills:**
- RED: Run pressure scenarios WITHOUT skill, document baseline behavior
- GREEN: Write skill addressing specific failures, re-test WITH skill
- REFACTOR: Close loopholes, add explicit counters to rationalizations

**Required checklist (use TodoWrite):**
- Create pressure scenarios (3+ combined pressures for discipline skills)
- Document baseline behavior verbatim
- Write skill with YAML frontmatter (name, description)
- Description starts with "Use when..." and includes triggers/symptoms
- Test scenarios WITH skill to verify compliance
- Close loopholes and re-test until bulletproof

**See:** `skills/writing-skills/SKILL.md` for complete methodology

### Modifying Existing Skills

**NEVER edit skills without testing first:**
- Run baseline test to verify current behavior
- Make changes
- Re-test to verify skill still works
- Test for new rationalizations

**Iron Law:** NO SKILL WITHOUT A FAILING TEST FIRST (applies to edits too)

## Test-Driven Development Rules

**Iron Law:** NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

**RED-GREEN-REFACTOR Cycle:**
1. RED: Write one minimal failing test
2. Verify RED: Watch it fail correctly (mandatory, never skip)
3. GREEN: Write simplest code to pass
4. Verify GREEN: Watch it pass (mandatory)
5. REFACTOR: Clean up while keeping tests green

**Common Violations to Avoid:**
- Code before test → Delete and start over
- Test passes immediately → You're testing existing behavior, fix test
- "I'll test after" → Tests-after verify what code does, not what it should do
- "Keep as reference" → You'll adapt it, that's testing after. Delete means delete
- Skipping watch-it-fail step → You don't know if test works

**See:** `skills/test-driven-development/SKILL.md`

## Structured Specifications

### Overview

Structured specs provide testable contracts between design and implementation. They are **optional** — the brainstorming skill offers them after design completion.

### Directory Convention

```
docs/specs/
  <feature>/                    # Per-feature working directory
    proposal.md                 # Intent, scope, impact, success criteria
    design.md                   # Technical decisions
    specs/
      <component>-delta.md      # Delta spec with GIVEN/WHEN/THEN scenarios
  _living/                      # Merged source of truth (post-archiving)
    <component>.md              # Current system behavior
  _archive/                     # Completed features
    YYYY-MM-DD-<feature>/       # Archived feature specs
```

### Delta Spec Format

```markdown
## ADDED
### <Behavior Name>
GIVEN [precondition] WHEN [action] THEN [result]

## MODIFIED
### <Behavior Name>
Was: [old] → Now: [new] → Reason: [why]
GIVEN ... WHEN ... THEN ...

## REMOVED
### <Behavior Name>
Was: [what] → Reason: [why]
```

### Workflow

1. **Write specs** (`/superpowerwithcodex:write-specs`) — after brainstorming, create structured specs
2. **Plan with scenarios** — writing-plans includes scenario tables when specs exist
3. **Execute with contracts** — Codex receives scenarios as inviolable requirements
4. **Verify specs** (`/superpowerwithcodex:verify-specs`) — check completeness, correctness, coherence
5. **Archive specs** (`/superpowerwithcodex:archive-specs`) — merge deltas into living specs, archive feature

### Key Files

- `skills/writing-specs/SKILL.md` - Spec authoring process
- `skills/verifying-specs/SKILL.md` - Three-check verification
- `skills/archiving-specs/SKILL.md` - Delta-to-living merge process

## Installation & Updates

**Install via Claude Code Plugin Marketplace:**
```bash
/plugin marketplace add anna-belle-zhang/superpowerwithcodex
/plugin install superpowerwithcodex@superpowerwithcodex
```

**Update:**
```bash
/plugin update superpowerwithcodex
```

**Verify installation:**
```bash
/help
# Should show:
# /superpowerwithcodex:brainstorm - Interactive design refinement
# /superpowerwithcodex:write-plan - Create implementation plan
# /superpowerwithcodex:execute-plan - Execute plan in batches
# /superpowerwithcodex:write-specs - Create structured specifications
# /superpowerwithcodex:verify-specs - Verify spec scenarios have tests
# /superpowerwithcodex:archive-specs - Archive delta specs into living specs
# /superpowerwithcodex:search - Search marketplace catalog
```

## Multi-Platform Support

- **Claude Code:** Native plugin system (preferred)
- **Codex:** Manual installation via `.codex/INSTALL.md`
- **OpenCode:** Manual installation via `.opencode/INSTALL.md`

## Key Principles for Contributors

**Skill Quality Standards:**
- Max 1024 chars total frontmatter (name + description)
- Description starts "Use when..." with specific triggers
- Written in third person for system prompt injection
- Token efficient (getting-started: <150 words, frequently-loaded: <200 words)
- Tested with subagents before deployment
- No narrative storytelling, only reusable patterns

**Code Quality Standards:**
- All features require tests first (TDD)
- One behavior per test
- Clear test names describing behavior
- Real code, minimal mocks
- Watch tests fail before implementing

**Documentation Standards:**
- Design docs: `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Implementation plans: Bite-sized tasks with verification steps
- All changes committed to git

## Important Files

- `lib/skills-core.js` - Core skill discovery and resolution logic
- `lib/codex-integration.js` - Codex dispatch, retry, and E2E strategy detection
- `lib/ralph-orchestrator.js` - Ralph-Codex-E2E loop orchestration
- `skills/claude-codex-specs-tdd/SKILL.md` - Specs-first dispatch workflow (Claude side)
- `skills/spec-driven-tdd/SKILL.md` - Spec-driven implementation (Codex side)
- `skills/writing-skills/SKILL.md` - Complete skill authoring guide
- `skills/test-driven-development/SKILL.md` - TDD methodology and enforcement
- `skills/brainstorming/SKILL.md` - Design refinement process
- `skills/writing-specs/SKILL.md` - Structured specification authoring
- `skills/verifying-specs/SKILL.md` - Spec verification (completeness, correctness, coherence)
- `skills/archiving-specs/SKILL.md` - Delta-to-living spec merge process
- `agents/code-reviewer.md` - Code review agent definition

## Philosophy Reminders

**Violating the letter of the rules is violating the spirit of the rules.**

When you think "skip TDD just this once" or "this skill is too simple to test" - that's rationalization. Follow the process. The systematic approach is the value.
