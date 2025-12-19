# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Superpowers is a complete software development workflow system for coding agents, built on composable "skills" that enforce systematic processes. It transforms how agents approach development by requiring design before code, comprehensive planning before implementation, and test-driven development throughout.

**Core Philosophy:**
- Test-Driven Development (write tests first, always)
- Systematic over ad-hoc (process over guessing)
- Complexity reduction (simplicity as primary goal)
- Evidence over claims (verify before declaring success)

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
- `hooks/hooks.json` - Session start hooks

**Commands:**
- `/superpowers:brainstorm` - Interactive design refinement
- `/superpowers:write-plan` - Create implementation plan
- `/superpowers:execute-plan` - Execute plan in batches

### Directory Structure

- `skills/` - All skill definitions (flat namespace)
- `commands/` - Slash command definitions
- `agents/` - Agent definitions (e.g., code-reviewer)
- `lib/` - Core utilities
- `hooks/` - Lifecycle hooks
- `docs/` - Documentation and design plans
- `tests/` - Test files

## Development Workflow

### The Superpowers Cycle

1. **brainstorming** - Before writing code, refine ideas through questions, explore alternatives, present design in sections. Saves to `docs/plans/YYYY-MM-DD-<topic>-design.md`

2. **using-git-worktrees** - After design approval, create isolated workspace on new branch, verify clean test baseline

3. **writing-plans** - Break work into 2-5 minute tasks with exact file paths, complete code, verification steps

4. **subagent-driven-development** or **executing-plans** - Dispatch fresh subagent per task or execute in batches with checkpoints

5. **test-driven-development** - Enforces RED-GREEN-REFACTOR cycle. Write failing test, watch it fail, write minimal code, watch it pass

6. **requesting-code-review** - Review against plan between tasks, block progress on critical issues

7. **finishing-a-development-branch** - Verify tests, present merge/PR options, cleanup

**CRITICAL: These workflows are mandatory, not suggestions. Skills are enforced processes.**

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

## Installation & Updates

**Install via Claude Code Plugin Marketplace:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**Update:**
```bash
/plugin update superpowers
```

**Verify installation:**
```bash
/help
# Should show:
# /superpowers:brainstorm - Interactive design refinement
# /superpowers:write-plan - Create implementation plan
# /superpowers:execute-plan - Execute plan in batches
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
- `skills/writing-skills/SKILL.md` - Complete skill authoring guide
- `skills/test-driven-development/SKILL.md` - TDD methodology and enforcement
- `skills/brainstorming/SKILL.md` - Design refinement process
- `agents/code-reviewer.md` - Code review agent definition

## Philosophy Reminders

**Violating the letter of the rules is violating the spirit of the rules.**

When you think "skip TDD just this once" or "this skill is too simple to test" - that's rationalization. Follow the process. The systematic approach is the value.
