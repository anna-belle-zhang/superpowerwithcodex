---
created: 2026-06-13
execution-strategy: claude-subagents
specs-dir: docs/specs/specs-workflow-skill-gaps/
---

# Specs Workflow Skill Gaps Fix — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the three structural gaps in the specs workflow skills (stale system index, dead debt pipeline, blind archive move) and remove regression-era authoring artifacts from the two skills written on 2026-03-12.

**Architecture:** All changes are edits to skill markdown in `skills/`. No production code. Verification is by grep against the edited files plus one subagent dry-run per `superpowerwithcodex:testing-skills-with-subagents` where noted.

**Analysis:** `docs/2026-06-13-specs-process-review-analysis.md` (findings #1, #2, #6, #7)

**Companion plan:** `E:\A\OpenMetadata\docs\plans\2026-06-13-specs-hardening-and-upstream-alignment.md` (repo catch-up + upstream alignment + March retrospective; execute after this plan so the new skill steps are exercised on the backfill)

---

### Task 1: Fix duplicated "If no:" branch in verifying-specs Step 4e

Regression-era editing artifact (finding #7): two contradictory "If no:" bullets.

**Files:**
- Modify: `skills/verifying-specs/SKILL.md:181-183`

**Step 1: Apply edit**

Old:
```markdown
- If yes: invoke `superpowers:cleanup-and-refactor`
- If no: continue to `superpowers:archiving-specs` with debt tracked for later
- If no: continue to `archive-specs` after verification
```

New:
```markdown
- If yes: invoke `superpowers:cleanup-and-refactor`
- If no: continue to `superpowers:archiving-specs` with debt tracked for later
```

**Step 2: Verify**

Run: `grep -c "^- If no:" skills/verifying-specs/SKILL.md`
Expected: `1`

**Step 3: Commit**

```bash
git add skills/verifying-specs/SKILL.md
git commit -m "fix(verifying-specs): remove duplicated contradictory Step 4e branch"
```

---

### Task 2: Make the DEBT annotation scan language-aware

The scan hardcodes C-style `// DEBT:` (`SKILL.md:105`), which never matches Python `# DEBT:` or SQL `-- DEBT:`. This is one of three reasons the debt pipeline has never fired (finding #2b).

**Files:**
- Modify: `skills/verifying-specs/SKILL.md` (lines 22, 100-113, 127)

**Step 1: Update the overview line (line 22)**

Old:
```markdown
4. **Debt identification** — collect `// DEBT:` annotations and behaviors replaced by REMOVED deltas
```

New:
```markdown
4. **Debt identification** — collect `DEBT:` annotations (any comment syntax), progress.md Issues entries, and behaviors replaced by REMOVED deltas
```

**Step 2: Update Step 4a scan command and prose**

Old:
```markdown
Scan the codebase for `// DEBT:` comments after verification passes:

```bash
rg -n "// DEBT:" src tests . 2>/dev/null
```
```

New:
```markdown
Scan the codebase for `DEBT:` comments after verification passes. Match every comment syntax in use (`#` Python/shell, `//` JS/Java, `--` SQL, `<!--` markdown/HTML):

```bash
rg -n "(#|//|--|<!--) ?DEBT:" src tests . 2>/dev/null
```
```

Also update the two later references to `// DEBT:` (lines 111 and 127) to read `DEBT:`.

**Step 3: Verify**

Run: `grep -c '// DEBT:' skills/verifying-specs/SKILL.md`
Expected: `0`
Run: `grep -c 'DEBT:' skills/verifying-specs/SKILL.md`
Expected: ≥ 6 (all generalized)

**Step 4: Commit**

```bash
git add skills/verifying-specs/SKILL.md
git commit -m "fix(verifying-specs): language-aware DEBT annotation scan"
```

---

### Task 3: Add progress.md Issues as a third debt source

Real debt lands in `progress.md` → `## Issues` (written by spec-driven-tdd), which verifying-specs never reads (finding #2). Add it as a scanned source.

**Files:**
- Modify: `skills/verifying-specs/SKILL.md` (insert new step after Step 4b, update skip condition)

**Step 1: Insert new Step 4b-2 after Step 4b**

```markdown
### Step 4b-2: Collect Debt from progress.md Issues

Read `docs/specs/<feature>/progress.md` and extract the `## Issues` section:

```bash
sed -n '/^## Issues/,/^## /p' docs/specs/<feature>/progress.md
```

Each non-empty entry describing a coverage compromise, shortcut, or deferred work is a debt candidate. Entries that merely narrate (e.g. "renamed X to Y") are not debt — judge by whether future work is implied.

If progress.md is missing or Issues is empty, continue. This alone is not a failure.
```

**Step 2: Update the skip condition in Step 4b**

Old:
```markdown
If there are no `REMOVED` sections and no `// DEBT:` comments:
```

New:
```markdown
If there are no `REMOVED` sections, no `DEBT:` comments, and no debt-bearing progress.md Issues entries:
```

(Note: the `// DEBT:` → `DEBT:` part overlaps Task 2 Step 2 — if Task 2 already changed this line, only add the Issues clause.)

**Step 3: Update the Technical Debt Summary block (around line 205)**

Add one line to the summary template:
```markdown
- progress.md Issues debt items found: K
```

**Step 4: Verify**

Run: `grep -n "Step 4b-2\|progress.md Issues" skills/verifying-specs/SKILL.md`
Expected: the new step heading plus ≥ 2 references.

**Step 5: Commit**

```bash
git add skills/verifying-specs/SKILL.md
git commit -m "feat(verifying-specs): scan progress.md Issues as debt source"
```

---

### Task 4: Instruct Codex to annotate debt at creation time

Nothing upstream ever tells Codex to write DEBT annotations, so the Task 2 scan has nothing to find (finding #2a). Add the instruction to the Codex-side skill.

**Files:**
- Modify: `skills/spec-driven-tdd/SKILL.md` (Step 3 list, ~line 55-62; Red Flags list, ~line 88-93)

**Step 1: Extend the Step 3 TDD loop list**

Old:
```markdown
1. **Write failing test** derived from GIVEN/WHEN/THEN (RED)
   - Assert the exact values from the spec
   - Run test — verify it FAILS before implementing
2. **Write minimal implementation** to make test pass (GREEN)
3. **If task involves external calls** — write integration test, verify passes
4. **Update progress.md**: `[ ]` → `[x]`, add commit hash
```

New:
```markdown
1. **Write failing test** derived from GIVEN/WHEN/THEN (RED)
   - Assert the exact values from the spec
   - Run test — verify it FAILS before implementing
2. **Write minimal implementation** to make test pass (GREEN)
3. **If task involves external calls** — write integration test, verify passes
4. **If you made a compromise** (coverage shortcut, mocked path that should be live, deferred edge case): add a `DEBT:` comment at the code site using the file's comment syntax (`# DEBT:` Python, `// DEBT:` JS/Java, `-- DEBT:` SQL) AND list it under `## Issues` in progress.md
5. **Update progress.md**: `[ ]` → `[x]`, add commit hash
```

**Step 2: Add to Red Flags list**

Append:
```markdown
- Making a coverage compromise without a `DEBT:` annotation + Issues entry
```

**Step 3: Verify**

Run: `grep -n "DEBT" skills/spec-driven-tdd/SKILL.md`
Expected: ≥ 2 matches (loop step + red flag).

**Step 4: Commit**

```bash
git add skills/spec-driven-tdd/SKILL.md
git commit -m "feat(spec-driven-tdd): require DEBT annotations for compromises"
```

---

### Task 5: archiving-specs — update the system index (ARCHITECTURE.md)

The root cause of finding #1: no skill maintains `_living/ARCHITECTURE.md`, so it drifted 6 weeks / 11 specs behind. Add an index-update step.

**Files:**
- Modify: `skills/archiving-specs/SKILL.md` (insert new step between Step 3 and Step 4; update Overview list and Step 5 report)

**Step 1: Update the Overview numbered list (lines 16-21)**

Old:
```markdown
1. ADDED scenarios → append to living spec
2. MODIFIED scenarios → replace in living spec
3. REMOVED scenarios → delete from living spec + record in change history
4. Move feature directory to archive
5. Commit
```

New:
```markdown
1. ADDED scenarios → append to living spec
2. MODIFIED scenarios → replace in living spec
3. REMOVED scenarios → delete from living spec + record in change history
4. Update the system index (ARCHITECTURE.md)
5. Move feature directory to archive
6. Commit
```

**Step 2: Insert new "Step 2.5: Update System Index" after Step 2**

```markdown
### Step 2.5: Update System Index

If `docs/specs/_living/ARCHITECTURE.md` exists:

1. For every living spec created or updated in Step 2, ensure the index has an entry: component name, link (`[component.md](component.md)`), and a 1-3 line summary of its key behaviors
2. If the feature introduces a new system area, add a new section/pillar following the existing structure
3. Update the "as of" date in the header to today

Every file in `docs/specs/_living/` (except ARCHITECTURE.md itself) must be reachable from the index. Verify:

```bash
for f in docs/specs/_living/*.md; do b=$(basename "$f"); [ "$b" = "ARCHITECTURE.md" ] && continue; grep -q "$b" docs/specs/_living/ARCHITECTURE.md || echo "NOT INDEXED: $b"; done
```

Expected: no output.

If ARCHITECTURE.md does not exist, skip this step (optionally offer to create it once ≥ 3 living specs exist).
```

**Step 3: Add to the Step 5 report template**

Add line:
```markdown
**System index:** updated / not present
```

**Step 4: Verify**

Run: `grep -n "ARCHITECTURE" skills/archiving-specs/SKILL.md | head -3`
Expected: ≥ 3 matches (overview, step, report).

**Step 5: Commit**

```bash
git add skills/archiving-specs/SKILL.md
git commit -m "feat(archiving-specs): maintain _living/ARCHITECTURE.md index"
```

---

### Task 6: archiving-specs — pre-archive completeness check

Step 3 is currently a blind `mv`, which let a missing progress.md, a stray root-level spec, and `progress copy.md` junk into the archive (findings #3, #5, #6).

**Files:**
- Modify: `skills/archiving-specs/SKILL.md` (insert before the (renumbered) archive-move step)

**Step 1: Insert "Step 2.6: Pre-Archive Completeness Check"**

```markdown
### Step 2.6: Pre-Archive Completeness Check

Before moving the feature directory, verify:

```bash
ls docs/specs/<feature>/
```

1. `progress.md` exists — if missing, STOP and ask whether to backfill a stub or proceed with a noted gap
2. `proposal.md` and `design.md` exist (warn if missing, not blocking)
3. Every `*.md` at the feature root is one of: proposal, design, progress, technical-debt, retrospective, or debug/journey notes — move stray delta/spec files into `specs/`
4. No junk files (`* copy.*`, editor backups) — delete them
```

**Step 2: Verify**

Run: `grep -n "Pre-Archive Completeness" skills/archiving-specs/SKILL.md`
Expected: 1 match.

**Step 3: Commit**

```bash
git add skills/archiving-specs/SKILL.md
git commit -m "feat(archiving-specs): pre-archive completeness check"
```

---

### Task 7: Full proofread of the two regression-era skills

The debt section of `verifying-specs` was authored 2026-03-12 (commit `91da369`), inside the regression window — Task 1's artifact may not be the only one (finding #7). `archiving-specs` was authored 2026-02-19, pre-window; proofread it too, on its own merits.

**Files:**
- Review (and fix in place): `skills/verifying-specs/SKILL.md`, `skills/archiving-specs/SKILL.md`

**Step 1: Read both files end-to-end checking for:**

1. Contradictory or duplicated branches (like Task 1's)
2. Broken cross-references — note both files reference skills under the `superpowers:` namespace (e.g. `superpowers:archiving-specs`) while this plugin's namespace is `superpowerwithcodex:`; confirm which namespace the installed plugin actually resolves and make all references consistent with it
3. Steps that reference files or sections that don't exist
4. Numbering gaps after Tasks 5-6 insertions (renumber Step 2.5/2.6/3/4/5 coherently)

**Step 2: Optional but recommended — subagent pressure-test**

Per `superpowerwithcodex:testing-skills-with-subagents`: dispatch a fresh subagent with a toy feature dir containing one all-ADDED delta, a progress.md with one Issues compromise, and a `# DEBT:` comment in a sample file; confirm the updated verifying-specs flow produces a `technical-debt.md` and the updated archiving-specs flow updates a stub ARCHITECTURE.md.

**Step 3: Commit**

```bash
git add skills/verifying-specs/SKILL.md skills/archiving-specs/SKILL.md
git commit -m "fix: proofread regression-era specs skills, consistent namespacing"
```

---

## Completion Criteria

- [ ] All 7 task verification greps pass
- [ ] No `// DEBT:` hardcoding remains anywhere in `skills/`
- [ ] `archiving-specs` overview lists 6 steps including index update
- [ ] Subagent dry-run (Task 7 Step 2) produces technical-debt.md and updates the index
- [ ] Companion OpenMetadata plan can then be executed using the updated skills
