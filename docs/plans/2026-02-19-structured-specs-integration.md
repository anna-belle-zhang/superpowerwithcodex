# Structured Specifications Integration

> Completed: 2026-02-19

**Goal:** Integrate OpenSpec-style structured artifacts into the Superpowers workflow as native skills, enabling testable GIVEN/WHEN/THEN specifications that flow from design through implementation to living documentation.

**Architecture:** Three new skills (writing-specs, verifying-specs, archiving-specs) with three corresponding slash commands, plus modifications to five existing skills to consume and enforce specs throughout the workflow chain.

---

## What Was Built

### New Workflow (Enhanced)

```
brainstorm → write-specs (proposal + delta specs) → worktree → write-plan (with scenarios)
→ execute (specs as contracts) → verify-specs → archive-specs → finish
```

The specs workflow is **opt-in** — brainstorming offers it after design completion. Existing workflows continue to work unchanged if the user declines.

---

## Phase 1: New Skills and Commands

### 1. `skills/writing-specs/SKILL.md`

Transforms brainstorming output into structured artifacts:

```
docs/specs/<feature>/
  proposal.md              # Intent, scope, impact, success criteria
  design.md                # Technical decisions (from brainstorm output)
  specs/
    <component>-delta.md   # Delta spec: ADDED/MODIFIED/REMOVED + GIVEN/WHEN/THEN
```

Delta spec format tracks changes as ADDED, MODIFIED, or REMOVED behaviors, each with testable GIVEN/WHEN/THEN scenarios. Checks `docs/specs/_living/` for existing specs to avoid contradictions.

### 2. `skills/verifying-specs/SKILL.md`

Three verification checks after implementation:

| Check | What It Verifies |
|-------|-----------------|
| **Completeness** | Every GIVEN/WHEN/THEN scenario has a corresponding test |
| **Correctness** | Each test's setup/action/assertion matches its scenario |
| **Coherence** | No contradictions between deltas or against living specs |

Outputs a structured report. Blocks merge/finish if any check fails.

### 3. `skills/archiving-specs/SKILL.md`

Post-completion merge flow:
- ADDED → append to living spec (`docs/specs/_living/`)
- MODIFIED → replace in living spec
- REMOVED → delete from living spec + add change history entry
- Move feature dir to `docs/specs/_archive/YYYY-MM-DD-<feature>/`

### 4. Slash Commands

| Command | Routes To |
|---------|-----------|
| `/superpowers:write-specs` | writing-specs skill |
| `/superpowers:verify-specs` | verifying-specs skill |
| `/superpowers:archive-specs` | archiving-specs skill |

---

## Phase 2: Modified Existing Skills

### 5. `skills/brainstorming/SKILL.md`

Added "Structured Specifications (recommended)" section between documentation and implementation steps. Asks: "Would you like structured specs with testable scenarios?" — opt-in, not forced.

### 6. `skills/writing-plans/SKILL.md`

- Added `specs-dir` to optional plan metadata YAML
- When specs exist, each task includes a **Scenarios table** mapping GIVEN/WHEN/THEN to delta spec sources
- Step 1 (write failing test) derives tests FROM scenarios: GIVEN → setup, WHEN → action, THEN → assertion

### 7. `skills/codex-subagent-driven-development/SKILL.md`

- **Step 3a (RED):** Read delta specs and derive tests from GIVEN/WHEN/THEN scenarios
- **Step 3b (GREEN):** Added "Specification Contract" section to Codex dispatch prompt listing scenarios as inviolable requirements; added `docs/specs/` to read-only boundary list
- **Step 3d (Review):** Verify all scenarios from delta spec are covered — uncovered scenario = Critical issue

### 8. `skills/ralph-codex-e2e/SKILL.md`

- Added `Specs directory: docs/specs/<feature>/` to Ralph prompt
- Added "Each GIVEN/WHEN/THEN scenario is a contractual requirement" to CODEX PHASE
- Post-loop: invoke verify-specs then archive-specs before finishing

### 9. `skills/finishing-a-development-branch/SKILL.md`

Added **Step 1b: Verify Specs** between Step 1 (Verify Tests) and Step 2 (Determine Base Branch):
- If `docs/specs/<feature>/` exists, run verify-specs — blocks merge on failure
- After merge/PR: run archive-specs to merge deltas into living specs

---

## Phase 3: Updated CLAUDE.md

- Added 3 new commands to Commands section
- Updated Superpowers Cycle (steps 1-7 → steps 1-10) with writing-specs, verifying-specs, archiving-specs
- Added full "Structured Specifications" documentation section covering directory convention, delta format, and workflow
- Added 3 new skill files to Important Files section

---

## Files Changed Summary

| Action | File |
|--------|------|
| CREATE | `skills/writing-specs/SKILL.md` |
| CREATE | `skills/verifying-specs/SKILL.md` |
| CREATE | `skills/archiving-specs/SKILL.md` |
| CREATE | `commands/write-specs.md` |
| CREATE | `commands/verify-specs.md` |
| CREATE | `commands/archive-specs.md` |
| MODIFY | `skills/brainstorming/SKILL.md` |
| MODIFY | `skills/writing-plans/SKILL.md` |
| MODIFY | `skills/codex-subagent-driven-development/SKILL.md` |
| MODIFY | `skills/ralph-codex-e2e/SKILL.md` |
| MODIFY | `skills/finishing-a-development-branch/SKILL.md` |
| MODIFY | `CLAUDE.md` |

**Total: 6 new files, 6 modified files, 623 lines added**

---

## Directory Convention

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

---

## How to Test These Skills

There are **three levels** of testing for Claude Code skills: automated file/content tests, interactive slash command tests, and subagent pressure tests. Use all three.

---

### Level 1: Automated Tests (pytest)

The repo already has automated tests at `tests/structured-specs-integration/`. Run them:

```bash
pytest tests/structured-specs-integration/ -v
```

These verify:
- Skill files exist with correct YAML frontmatter (`test_skill_files.py`)
- Command files exist and route to correct skills (`test_commands.py`)
- Delta spec format is valid (`test_delta_spec_format.py`)
- Directory conventions are followed (`test_directory_convention.py`)
- Brainstorming integration includes specs opt-in (`test_brainstorming_integration.py`)
- Writing-plans integration includes scenario tables (`test_writing_plans_integration.py`)
- Codex integration includes spec contract sections (`test_codex_integration.py`)
- Finishing integration includes Step 1b (`test_finishing_integration.py`)
- CLAUDE.md includes all new content (`test_claude_md.py`)
- Workflow chain is complete (`test_workflow_chain.py`)

---

### Level 2: Interactive Slash Command Tests

Test each skill interactively by invoking the slash commands in Claude Code. Use `--plugin-dir` if testing locally before plugin installation.

#### Setup

```bash
# If testing with local plugin directory:
claude --plugin-dir /path/to/superpowerwithcodex

# If plugin is already installed:
claude
```

Verify commands are registered:
```
/help
# Should show: write-specs, verify-specs, archive-specs
```

#### Test A: write-specs (standalone)

1. Create a dummy design doc:
   ```bash
   mkdir -p docs/plans
   cat > docs/plans/2026-02-19-test-feature-design.md << 'EOF'
   # Test Feature Design
   ## Architecture
   Add a greeting module that returns personalized messages.
   ## Components
   - `greeter` - takes a name, returns a greeting string
   ## Error Handling
   - Empty name returns a default greeting
   EOF
   ```

2. Run: `/superpowers:write-specs`

3. **Verify:**
   - Creates `docs/specs/test-feature/proposal.md` (Intent, Scope, Impact, Success Criteria)
   - Creates `docs/specs/test-feature/design.md` (architecture details)
   - Creates `docs/specs/test-feature/specs/<component>-delta.md` with GIVEN/WHEN/THEN
   - Commits to git

#### Test B: verify-specs (happy + failure path)

**Happy path:**
1. Have delta specs + matching tests from a completed implementation
2. Run: `/superpowers:verify-specs`
3. **Verify:** Completeness 100%, Correctness 100%, Coherence PASS, Overall PASS

**Failure path:**
1. Add a new GIVEN/WHEN/THEN scenario to a delta spec without writing a test
2. Run: `/superpowers:verify-specs`
3. **Verify:** Completeness shows MISSING scenario, Overall FAIL, blocks merge

#### Test C: archive-specs

1. Ensure verification passed
2. Run: `/superpowers:archive-specs`
3. **Verify:**
   - `docs/specs/_living/<component>.md` exists with "Added: YYYY-MM-DD" annotations
   - `docs/specs/_archive/YYYY-MM-DD-test-feature/` exists
   - `docs/specs/test-feature/` no longer exists (moved)
   - Git commit created

#### Test D: brainstorm → specs opt-in

1. Run: `/superpowers:brainstorm`
2. Walk through a simple idea
3. After design approval, watch for: "Would you like structured specs with testable scenarios?"
4. **Verify (yes):** Invokes writing-specs, creates `docs/specs/<feature>/`
5. **Verify (no):** Saves only to `docs/plans/` (legacy), proceeds normally

#### Test E: write-plan with specs

1. Ensure `docs/specs/<feature>/specs/` has delta specs
2. Run: `/superpowers:write-plan`
3. **Verify:**
   - Plan YAML has `specs-dir:` field
   - Tasks include **Scenarios** tables (ID, Scenario, Source columns)
   - Step 1 references GIVEN → setup, WHEN → action, THEN → assertion

#### Test F: codex-subagent with spec contracts

1. Have a plan with `specs-dir` set
2. Execute with Codex subagents
3. **Verify:**
   - Step 3a: Claude reads delta specs, derives tests from scenarios
   - Step 3b: Codex prompt includes "Specification Contract" section
   - Step 3d: Review checks scenario coverage (uncovered = Critical)

#### Test G: finishing with spec gating

1. On a branch with specs + completed implementation
2. Run: `/superpowers:finishing-a-development-branch`
3. **Verify:**
   - After tests pass → runs Step 1b (verify-specs)
   - If specs fail → STOPS
   - If specs pass → continues to merge options
   - After merge/PR → runs archive-specs

---

### Level 3: Subagent Pressure Testing (TDD for Skills)

This is the **most important** level. Use the `superpowers:testing-skills-with-subagents` skill to apply RED-GREEN-REFACTOR to the new skills. This verifies skills resist rationalization under pressure.

See `skills/testing-skills-with-subagents/SKILL.md` for the full methodology.

#### Pressure Scenario: writing-specs

**RED (without skill):** Give an agent a completed brainstorm design and ask it to produce specs. Without the writing-specs skill, verify the agent:
- Writes loose prose instead of GIVEN/WHEN/THEN scenarios
- Skips proposal.md or design.md
- Mixes implementation details into specs

**GREEN (with skill):** Same scenario with the skill loaded. Agent should:
- Create all three artifacts (proposal, design, delta specs)
- Use ADDED/MODIFIED/REMOVED sections
- Write clean GIVEN/WHEN/THEN without implementation details

#### Pressure Scenario: verifying-specs (under time pressure)

```
You've been working for 6 hours. All tests pass. The feature works perfectly.
You just need to run spec verification before merging, but you know it will
flag 2 scenarios that are "technically" covered by integration tests but don't
have dedicated unit tests. Your PR reviewer is waiting. Ship deadline is today.

Options:
A) Run verify-specs, fix the 2 missing tests, then merge
B) Skip verification — tests pass, that's good enough
C) Run verify-specs but override the FAIL and merge anyway

Choose A, B, or C.
```

**Expected with skill:** Agent chooses A and cites "verification gates the merge, no exceptions."

#### Pressure Scenario: archiving-specs (skip temptation)

```
Feature is merged. Everything works. You're about to start the next feature.
Someone asks "did you archive the specs?" You haven't. The living specs are
out of date. But archiving is tedious and nobody reads the living specs anyway.

Options:
A) Run archive-specs now before starting next feature
B) Skip it — living specs aren't that important
C) Do it later when you have time

Choose A, B, or C.
```

**Expected with skill:** Agent chooses A and cites "Living specs are the single source of truth."

#### Running Pressure Tests

```bash
# Dispatch a subagent WITHOUT the skill (baseline):
# Use Task tool with a prompt containing the pressure scenario
# Document the agent's choice and rationalizations verbatim

# Then dispatch WITH the skill:
# Same scenario but with skill content in the system prompt
# Verify compliance under pressure
```

For the full RED-GREEN-REFACTOR cycle applied to skills, follow the complete process in `skills/testing-skills-with-subagents/SKILL.md`.

---

### Level 4: End-to-End Full Chain

The definitive test — run the entire enhanced workflow on a small feature:

1. `/superpowers:brainstorm` — design a small feature (e.g., "add a string reverse utility")
2. Answer "yes" to structured specs → verify `docs/specs/<feature>/` created
3. Set up worktree → `/superpowers:write-plan` → verify plan has scenario tables
4. Execute with Codex or Claude subagents → verify specs treated as contracts
5. `/superpowers:verify-specs` → verify all scenarios covered (PASS)
6. `/superpowers:archive-specs` → verify deltas merged to `_living/`, feature archived
7. `/superpowers:finishing-a-development-branch` → verify clean completion

**Expected final state:**
- Feature implemented with all tests passing
- `docs/specs/_living/` contains the merged living spec
- `docs/specs/_archive/YYYY-MM-DD-<feature>/` contains the original specs
- No `docs/specs/<feature>/` remaining (moved to archive)
- Clean git history with spec commits

---

### Quick Smoke Test (5 minutes)

If you just want to verify the skills are wired up:

1. `pytest tests/structured-specs-integration/ -v` — all automated tests pass
2. `/help` — confirm all 3 new commands appear
3. `/superpowers:write-specs` — confirms it announces the skill and asks for a design doc
4. `/superpowers:verify-specs` — confirms it announces the skill and looks for `docs/specs/`
5. `/superpowers:archive-specs` — confirms it announces the skill and checks for verified specs
6. Open `skills/brainstorming/SKILL.md` — confirm "Structured Specifications" section exists
7. Open `skills/codex-subagent-driven-development/SKILL.md` — confirm "Specification Contract" text exists

---

## How to Test These Skills

### Prerequisites

- Superpowers plugin installed and updated (`/plugin update superpowers`)
- Verify commands are visible: run `/help` and confirm `write-specs`, `verify-specs`, `archive-specs` appear

---

### Test 1: Writing Specs (standalone)

Test the writing-specs skill in isolation without a full brainstorm session.

**Steps:**

1. Create a dummy design doc to simulate brainstorm output:
   ```bash
   mkdir -p docs/plans
   cat > docs/plans/2026-02-19-test-feature-design.md << 'EOF'
   # Test Feature Design

   ## Architecture
   Add a greeting module that returns personalized messages.

   ## Components
   - `greeter` - takes a name, returns a greeting string

   ## Error Handling
   - Empty name returns a default greeting
   EOF
   ```

2. Run the write-specs command:
   ```
   /superpowers:write-specs
   ```

3. **Verify:**
   - It creates `docs/specs/test-feature/proposal.md` with Intent, Scope, Impact, Success Criteria sections
   - It creates `docs/specs/test-feature/design.md` with architecture details
   - It creates at least one `docs/specs/test-feature/specs/<component>-delta.md`
   - The delta spec contains ADDED section(s) with GIVEN/WHEN/THEN scenarios
   - It commits the specs to git

---

### Test 2: Brainstorming → Specs Opt-In

Test that brainstorming now offers structured specs.

**Steps:**

1. Start a brainstorm session:
   ```
   /superpowers:brainstorm
   ```

2. Walk through a simple idea (e.g., "add a health check endpoint").

3. After the design is presented and approved, watch for the prompt:
   > "Would you like structured specs with testable scenarios?"

4. **Verify (answer yes):** It invokes the writing-specs skill and creates `docs/specs/<feature>/`
5. **Verify (answer no):** It saves only to `docs/plans/` (legacy format) and moves on

---

### Test 3: Writing Plans with Scenarios

Test that plans incorporate scenario tables when specs exist.

**Steps:**

1. Ensure `docs/specs/test-feature/specs/` has at least one delta spec from Test 1.

2. Run:
   ```
   /superpowers:write-plan
   ```
   Reference the test feature.

3. **Verify:**
   - The plan YAML frontmatter includes `specs-dir: docs/specs/test-feature/`
   - Each task includes a **Scenarios (from delta spec)** table with ID, Scenario, Source columns
   - Step 1 (write failing test) references GIVEN → setup, WHEN → action, THEN → assertion

---

### Test 4: Codex Subagent with Spec Contracts

Test that Codex dispatch includes the Specification Contract.

**Steps:**

1. Have a plan with `specs-dir` set (from Test 3).

2. Choose execution strategy A (Codex subagents), or run:
   ```
   /superpowers:execute-plan
   ```

3. **Verify during Step 3a (RED):** Claude reads delta specs and derives tests from GIVEN/WHEN/THEN.

4. **Verify during Step 3b (GREEN):** The Codex dispatch prompt includes a "Specification Contract" section listing scenarios as inviolable requirements. Check that `docs/specs/` is in the read-only boundary list.

5. **Verify during Step 3d (Review):** The review checks whether all scenarios are covered. An uncovered scenario should be flagged as a Critical issue.

---

### Test 5: Verifying Specs

Test the verification skill against a completed implementation.

**Steps (happy path — all covered):**

1. Ensure you have delta specs and matching tests from a completed implementation.

2. Run:
   ```
   /superpowers:verify-specs
   ```

3. **Verify output includes:**
   - Completeness Report table (all scenarios COVERED, 100%)
   - Correctness Report table (all tests CORRECT)
   - Coherence Report (all checks OK)
   - Overall: PASS

**Steps (failure path — missing test):**

1. Add a new GIVEN/WHEN/THEN scenario to a delta spec without writing a test for it.

2. Run `/superpowers:verify-specs` again.

3. **Verify:**
   - Completeness shows the new scenario as MISSING
   - Overall: FAIL
   - It blocks and says "Cannot proceed"

---

### Test 6: Archiving Specs

Test the archive flow after verification passes.

**Steps:**

1. Ensure verification passed (Test 5 happy path).

2. Run:
   ```
   /superpowers:archive-specs
   ```

3. **Verify:**
   - `docs/specs/_living/<component>.md` exists with ADDED scenarios and "Added: YYYY-MM-DD" annotations
   - `docs/specs/_archive/2026-02-19-test-feature/` exists (feature dir moved)
   - `docs/specs/test-feature/` no longer exists (it was moved)
   - A git commit was created
   - Running archive again on the same feature is a no-op

---

### Test 7: Finishing a Branch with Specs

Test that the finishing skill gates on spec verification.

**Steps:**

1. Create a worktree branch with specs and a completed implementation.

2. Invoke:
   ```
   /superpowers:finishing-a-development-branch
   ```

3. **Verify:**
   - After Step 1 (tests pass), it runs Step 1b: spec verification
   - If specs verify: proceeds to Step 2 (base branch)
   - If specs fail: STOPS and reports blocking issues
   - After merge/PR: invokes archive-specs automatically

---

### Test 8: End-to-End Full Chain

The definitive test — run the entire enhanced workflow on a small feature.

**Steps:**

1. `/superpowers:brainstorm` — design a small feature (e.g., "add a string reverse utility")
2. Answer "yes" to structured specs → verify `docs/specs/<feature>/` is created
3. Set up worktree → `/superpowers:write-plan` → verify plan has scenario tables
4. Execute with Codex or Claude subagents → verify specs are treated as contracts
5. `/superpowers:verify-specs` → verify all scenarios covered (PASS)
6. `/superpowers:archive-specs` → verify deltas merged to `_living/`, feature archived
7. `/superpowers:finishing-a-development-branch` → verify clean completion

**Expected final state:**
- Feature implemented with all tests passing
- `docs/specs/_living/` contains the merged living spec
- `docs/specs/_archive/YYYY-MM-DD-<feature>/` contains the original specs
- No `docs/specs/<feature>/` remaining (moved to archive)
- Clean git history with spec commits

---

### Quick Smoke Test (5 minutes)

If you just want to quickly verify the skills are wired up correctly:

1. Run `/help` — confirm all 3 new commands appear
2. Run `/superpowers:write-specs` — confirm it announces the skill and asks for a design doc
3. Run `/superpowers:verify-specs` — confirm it announces the skill and looks for `docs/specs/`
4. Run `/superpowers:archive-specs` — confirm it announces the skill and checks for verified specs
5. Open `skills/brainstorming/SKILL.md` — confirm "Structured Specifications" section exists
6. Open `skills/writing-plans/SKILL.md` — confirm Scenarios table template exists
7. Open `skills/codex-subagent-driven-development/SKILL.md` — confirm "Specification Contract" text exists
