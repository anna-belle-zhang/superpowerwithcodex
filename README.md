# Superpowers with Codex Integration

**Fork of [obra/superpowers](https://github.com/obra/superpowers) with Codex MCP integration**

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

### 3. **Multimodal Analysis** (`gemini-cli`)
- ✅ **Analyze Images**: UI/UX feedback, diagram explanation
- ✅ **Process Documents**: PDF summarization, long-form content
- ✅ **Audio/Video**: Transcription, content extraction
- ✅ **Codebase Scanning**: Security audits, architecture analysis
- ✅ **Context Isolation**: Long output stays in agent, only summaries returned

📖 [Gemini Integration Guide](docs/gemini-cli-integration.md)

### 4. **Quick Coding Tasks** (`codex-cli`)
- ✅ **One-Off Implementations**: Single functions, quick features
- ✅ **Bug Fixes**: Targeted fixes with file boundaries
- ✅ **File Creation**: Generate utilities from descriptions
- ✅ **Fast Iteration**: No full TDD when you need speed
- ✅ **Boundary Enforcement**: Strict writable vs read-only control

📖 [Codex CLI Guide](docs/codex-cli-integration.md)

## How it works

It starts from the moment you fire up your coding agent. As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do. 

Once it's teased a spec out of the conversation, it shows it to you in chunks short enough to actually read and digest. 

After you've signed off on the design, your agent puts together an implementation plan that's clear enough for an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing to follow. It emphasizes true red/green TDD, YAGNI (You Aren't Gonna Need It), and DRY. 

Next up, once you say "go", it launches a *subagent-driven-development* process, having agents work through each engineering task, inspecting and reviewing their work, and continuing forward. It's not uncommon for Claude to be able to work autonomously for a couple hours at a time without deviating from the plan you put together.

There's a bunch more to it, but that's the core of the system. And because the skills trigger automatically, you don't need to do anything special. Your coding agent just has Superpowers.


## Sponsorship

If Superpowers has helped you do stuff that makes money and you are so inclined, I'd greatly appreciate it if you'd consider [sponsoring my opensource work](https://github.com/sponsors/obra).

Thanks! 

- Jesse


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

This is a private repo — install via symlink from your local checkout (skills update instantly, no sync needed):

**Step 1 — Symlink local repo into Codex's skills directory:**
```bash
ln -s /path/to/your/superpowerwithcodex ~/.codex/superpowerwithcodex
```
Replace `/path/to/your/superpowerwithcodex` with the actual path where you cloned this repo.

**Step 2 — Create personal skills directory:**
```bash
mkdir -p ~/.codex/skills
```

**Step 3 — Add to `~/.codex/AGENTS.md`:**
```markdown
## Superpowerwithcodex System

<EXTREMELY_IMPORTANT>
You have superpowers. Superpowers teach you new skills and capabilities. RIGHT NOW run: `~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap` and follow the instructions it returns.
</EXTREMELY_IMPORTANT>
```

**Step 4 — Verify:**
```bash
~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap
```

You should see skill listings. Codex will now automatically discover and load `superpowerwithcodex:spec-driven-tdd` when dispatched by Claude via `claude-codex-specs-tdd`.

**Detailed docs:** [docs/README.codex.md](docs/README.codex.md)

### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
```

**Detailed docs:** [docs/README.opencode.md](docs/README.opencode.md)

## Codex Integration (Optional)

Superpowers can use Codex subagents for implementation in a strict TDD workflow where Claude writes tests and reviews.

- Setup and workflow: [docs/codex-integration.md](docs/codex-integration.md)
- Skill: `superpowerwithcodex:codex-subagent-driven-development`

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
   - **D) Parallel session**: Separate session with batch execution and checkpoints
   - **E) Ralph-Codex-E2E**: Fully autonomous loop (walk away)

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

## The Basic Workflow

1. **brainstorming** - Activates before writing code. Refines rough ideas through questions, explores alternatives, presents design in sections for validation. Saves design document.

2. **using-git-worktrees** - Activates after design approval. Creates isolated workspace on new branch, runs project setup, verifies clean test baseline.

3. **writing-plans** - Activates with approved design. Breaks work into bite-sized tasks (2-5 minutes each). Every task has exact file paths, complete code, verification steps.

4. **codex-subagent-driven-development**, **subagent-driven-development**, or **executing-plans** - Activates with plan. Uses Codex for implementation (optional) or dispatches fresh subagent per task (same session, fast iteration) or executes in batches (parallel session, human checkpoints).

5. **test-driven-development** - Activates during implementation. Enforces RED-GREEN-REFACTOR: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests.

6. **requesting-code-review** - Activates between tasks. Reviews against plan, reports issues by severity. Critical issues block progress.

7. **finishing-a-development-branch** - Activates when tasks complete. Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree.

**The agent checks for relevant skills before any task.** Mandatory workflows, not suggestions.

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

### Tests-First Feature Development
```bash
# Design first
User: /superpowerwithcodex:brainstorm Build a user authentication system

# Plan implementation
User: /superpowerwithcodex:write-plan Create the auth system

# Execute with TDD (Claude writes tests, Codex implements, Claude reviews)
User: Execute with codex-subagent-driven-development
```

### Quick Coding Tasks
```bash
# Implement single function
User: Use Codex to implement fibonacci in src/utils/math.py

# Fix specific bug
User: Codex fix the off-by-one error in routes.py:45

# Create utility file
User: Let Codex create a logger utility with rotation
```

### Multimodal Analysis
```bash
# Analyze image
User: Use Gemini to analyze screenshot.png for UI issues

# Summarize document
User: Gemini help me summarize research-paper.pdf

# Scan codebase
User: Let Gemini scan ./src for security vulnerabilities
```

### Combined Workflow
```bash
# 1. Research with Gemini
User: Use Gemini to analyze competitor-ui.png

# 2. Design with Claude
User: /superpowerwithcodex:brainstorm Design our UI based on insights

# 3. Quick utilities with Codex
User: Use Codex to create theme.css

# 4. Main feature with full TDD
User: Execute implementation plan with codex-subagent-driven-development
```

## What's Inside

### Skills Library

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle
- **condition-based-waiting** - Async test patterns
- **testing-anti-patterns** - Common pitfalls to avoid

**Debugging** 
- **systematic-debugging** - 4-phase root cause process
- **root-cause-tracing** - Find the real problem
- **verification-before-completion** - Ensure it's actually fixed
- **defense-in-depth** - Multiple validation layers

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

**Technical Debt Management**
- **cleanup-and-refactor** *(Claude)* - Orchestrates debt removal in isolated worktree
- **code-simplification** *(Codex)* - Executes debt removal + static analysis + refactoring

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
