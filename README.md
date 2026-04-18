# Superpowers with Codex Integration

**Fork of [obra/superpowers](https://github.com/obra/superpowers) with Codex, open-specs integration**

Superpowers is a complete software development workflow for your coding agents, built on top of composable "skills". This fork adds **Codex integration** enabling two powerful TDD workflows:

**Specs-first workflow** (recommended):
- **Claude writes specs** (GIVEN/WHEN/THEN contracts) and runs E2E tests
- **Codex reads specs, writes its own plan + unit + integration tests, implements**

**Tests-first workflow** (when you need human review between tasks):
- **Claude writes the tests** (enforcing TDD best practices)
- **Codex implements the code** (via MCP protocol)
- **Claude reviews and validates** (quality gates with code review)

## 🆕 What's New: Four Integration Patterns

This fork adds **three powerful integration patterns** following the thin skill + thick executor architecture:

### 1. **Specs-First Workflow** (`claude-codex-specs-tdd` + `spec-driven-tdd`)

The recommended workflow. Claude writes specs; Codex does everything else.

- ✅ **Claude writes specs**: GIVEN/WHEN/THEN scenarios as contractual requirements
- ✅ **Codex reads specs**: derives its own plan, unit tests, and integration tests
- ✅ **Single dispatch**: Claude sends spec path — Codex runs autonomously
- ✅ **Progress tracking**: Codex saves `progress.md` in the spec folder
- ✅ **E2E by Claude**: Claude runs end-to-end tests after Codex returns
- ✅ **Mid-cycle re-entry**: re-enter at any point to fix issues or update specs

**Claude Code skill**: `superpowerwithcodex:claude-codex-specs-tdd`
**Codex skill** (loaded by Codex automatically): `superpowerwithcodex:spec-driven-tdd`

**Full workflow:**
```
brainstorm → write-specs → dispatch Codex → Codex: reads specs, writes plan,
             TDD loop, updates progress.md → Claude: E2E tests → verify-specs
```

### 2. **Tests-First TDD Workflow** (`codex-subagent-driven-development`)
- ✅ **Strict TDD**: RED (Claude tests) → GREEN (Codex implements) → REFACTOR (Claude reviews)
- ✅ **File Boundary Protection**: Tests and configs are protected from modification
- ✅ **Retry Chain**: Automatic retry with research guidance on failures
- ✅ **Quality Gates**: Code review after each implementation task
- ✅ **Clean Git History**: Separate commits for tests and implementation

📖 [Complete Guide](docs/quickstart-codex-subagent-workflow.md)

## Installation

**Note:** Installation differs by platform. Claude Code has a built-in plugin system. Codex and OpenCode require manual setup.

### Claude Code (via Plugin Marketplace)

In Claude Code, register the marketplace first:

```bash
/plugin marketplace add anna-belle-zhang/superpowerwithcodex
```

Then install the plugin from this marketplace:

```bash
/plugin install superpowerwithcodex@superpowerwithcodex
```

**For Codex Integration**: See [docs/codex-integration.md](docs/codex-integration.md) for MCP server setup.

### Verify Installation

Check that commands appear:

```bash
/help
```

```
# Should see:
# /superpowerwithcodex:brainstorm   - Interactive design refinement
# /superpowerwithcodex:write-plan   - Create implementation plan
# /superpowerwithcodex:execute-plan - Execute plan in batches
# /superpowerwithcodex:write-specs  - Create structured specifications
# /superpowerwithcodex:verify-specs - Verify spec scenarios have tests
# /superpowerwithcodex:archive-specs - Archive delta specs into living specs
# /superpowerwithcodex:cleanup-and-refactor - Clean tracked technical debt in isolated worktree
```

### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/anna-belle-zhang/superpowerwithcodex/refs/heads/main/.codex/INSTALL.md
```

**Detailed docs:** [docs/README.codex.md](docs/README.codex.md)

### GitHub Copilot CLI

```bash
copilot plugin marketplace add anna-belle-zhang/superpowerwithcodex
copilot plugin install superpowerwithcodex@superpowerwithcodex
```

## Codex Integration (Optional)

Superpowers can use Codex subagents for implementation in a strict TDD workflow where Claude writes tests and reviews.

- Setup and workflow: [docs/codex-integration.md](docs/codex-integration.md)
- Full plugin reference: [docs/codex-plugin.md](docs/codex-plugin.md)
- Skill: `superpowerwithcodex:codex-subagent-driven-development`

### Codex Permissions

Codex runs inside a sandbox. **Write access is not on by default** — you must configure it in `~/.codex/config.toml`.

| Sandbox mode | File writes | When to use |
|---|---|---|
| `read-only` | No | Review, diagnosis only |
| `workspace-write` | Project dir only | Implementation tasks (required for TDD) |
| `danger-full-access` | Unrestricted | Only in externally sandboxed environments |

**Minimum required config** for implementation tasks:

```toml
# ~/.codex/config.toml
[sandbox_workspace_write]
network_access = true   # needed for package managers, test suites hitting external services
```

Without `workspace-write`, Codex can read but cannot write files. Without `network_access = true`, package installs and API-dependent tests will fail silently.

**How write access flows:**
```
Agent(codex:codex-rescue)
  └─ Bash: node codex-companion.mjs task --write [prompt]
       └─ Codex app-server (sandbox: workspace-write)
```

The `--write` flag is passed automatically by the skills. You only need to configure the sandbox mode once in `~/.codex/config.toml`.

See [docs/codex-plugin.md](docs/codex-plugin.md) for troubleshooting network and permission issues.

## End-to-End Full Chain (with Structured Specs)

The complete workflow for a new feature using structured specifications:

```
brainstorm → write-specs → worktree → write-plan → execute → verify-specs → cleanup-and-refactor? → archive-specs → finish
```

**Step-by-step:**

1. **Design** — `/superpowerwithcodex:brainstorm <your idea>`
   - Refines idea through questions, presents design in sections for approval
   - Saves design to `docs/plans/YYYY-MM-DD-<feature>-design.md`

2. **Structured specs** (opt-in) — `/superpowerwithcodex:write-specs`
   - Creates `docs/specs/<feature>/proposal.md`, `design.md`, and `specs/<component>-delta.md`
   - Each delta spec has GIVEN/WHEN/THEN scenarios — testable contracts

3. **Isolated workspace** — `/superpowerwithcodex:using-git-worktrees`
   - Creates a git worktree on a new feature branch
   - Verifies clean test baseline before work starts

4. **Implementation plan** — `/superpowerwithcodex:write-plan`
   - Breaks work into 2-5 minute tasks with exact file paths and code
   - When specs exist, each task includes a scenario table from delta specs

5. **Execute** — choose a strategy:
   - **A) Specs-first** (recommended): Claude writes specs → Codex reads specs, plans, tests, implements → Claude runs E2E
   - **B) Tests-first**: Claude writes tests → Codex implements → Claude reviews
   - **C) Claude subagents**: Fresh subagent per task with review between tasks

6. **Verify specs** — `/superpowerwithcodex:verify-specs`
   - **Completeness:** every GIVEN/WHEN/THEN scenario has a passing test
   - **Correctness:** each test's setup/action/assertion matches its scenario
   - **Coherence:** no contradictions between delta specs or living specs
   - **Technical Debt:** collects `// DEBT:` annotations + scenario-driven debt (REMOVED behaviors)
   - Creates `technical-debt.md` + updates `_technical-debt.md` tracker
   - Prompts: "Run cleanup-and-refactor now? (yes/no)"
   - Blocks merge on verification failure — no exceptions

7. **Technical debt cleanup** (optional) — `/superpowerwithcodex:cleanup-and-refactor <feature>`
   - **Isolated worktree:** Creates `cleanup/<feature>` branch for safe removal
   - **Codex execution:** Dispatches Codex with `code-simplification` skill
     - Phase 1: Remove debt items (files, obsolete code)
     - Phase 2: Static analysis (feature-scoped, finds unused code)
     - Phase 3: Refactoring (extract duplicates → reduce complexity → apply patterns)
   - **Automated verification:** Build + test before merge
   - **Merge options:** Auto-merge | Create PR | Manual review | Abort
   - **Status tracking:** Updates `_technical-debt.md` (Pending → In Progress → Completed/Failed)

8. **Finish branch** — `/superpowerwithcodex:finishing-a-development-branch`
   - Presents merge / PR / keep / discard options
   - Automatically runs archive-specs after merge

9. **Archive specs** — `/superpowerwithcodex:archive-specs`
   - Merges delta specs into `docs/specs/_living/` (source of truth)
   - Moves feature dir to `docs/specs/_archive/YYYY-MM-DD-<feature>/`

**Structured specs are opt-in.** The brainstorming skill asks after design approval. If you skip specs, steps 2, 6, and 8 are omitted and the workflow is: brainstorm → worktree → write-plan → execute → finish.

---

## Quick Usage Examples

### Specs-First Feature Development (Recommended)
```bash
# 1. Design
User: /superpowerwithcodex:brainstorm Build a user authentication system

# 2. Write specs (GIVEN/WHEN/THEN)
User: /superpowerwithcodex:write-specs

# 3. Claude dispatches Codex — Codex reads specs, writes plan + tests, implements
User: /superpowerwithcodex:claude-codex-specs-tdd
# → Codex loads spec-driven-tdd, reads docs/specs/auth/, writes progress.md
# → Claude runs E2E tests, validates spec coverage
```

## What's Inside

### Skills Library

**Debugging** 
- **systematic-debugging** - 4-phase root cause process
- **root-cause-tracing** - Find the real problem
- **verification-before-completion** - Ensure it's actually fixed
- **defense-in-depth** - Multiple validation layers

**Technical Debt Management**
- **cleanup-and-refactor** *(Claude)* - Orchestrates debt removal in isolated worktree
- **code-simplification** *(Codex)* - Executes debt removal + static analysis + refactoring


**Collaboration**
- **brainstorming** - Socratic design refinement
- **writing-specs** - Structured GIVEN/WHEN/THEN specifications
- **verifying-specs** - Completeness/correctness/coherence + debt identification
- **archiving-specs** - Merge deltas into living specs
- **writing-plans** - Detailed implementation plans
- **executing-plans** - Batch execution with checkpoints
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist
- **receiving-code-review** - Responding to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow
- **subagent-driven-development** - Fast iteration with quality gates

**External Tool Integration**
- **claude-codex-specs-tdd** - Claude writes specs, dispatches Codex, runs E2E (recommended)
- **spec-driven-tdd** *(Codex skill)* - Codex reads specs, writes plan, TDD loop, saves progress.md
- **codex-subagent-driven-development** - Claude writes tests, Codex implements, Claude reviews
- **codex-cli** - One-off Codex tasks (implement, fix, create)
- **gemini-cli** - Multimodal analysis (images, PDFs, audio, video, codebases)

**Meta** 
- **writing-skills** - Create new skills following best practices
- **testing-skills-with-subagents** - Validate skill quality
- **using-superpowers** - Introduction to the skills system

## Philosophy

- **Test-Driven Development** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

Read more: [Superpowers for Claude Code](https://blog.fsck.com/2025/10/09/superpowers/)

## Contributing

Skills live directly in this repository. To contribute:

1. Fork the repository
2. Create a branch for your skill
3. Follow the `writing-skills` skill for creating new skills
4. Use the `testing-skills-with-subagents` skill to validate quality
5. Submit a PR

See `skills/writing-skills/SKILL.md` for the complete guide.

## Updating

Skills update automatically when you update the plugin:

```bash
/plugin update superpowerwithcodex
```

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: https://github.com/obra/superpowers/issues
- **Marketplace**: https://github.com/obra/superpowers-marketplace
