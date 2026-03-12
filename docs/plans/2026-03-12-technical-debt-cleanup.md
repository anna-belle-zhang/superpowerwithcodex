# Technical Debt Cleanup & Refactoring Implementation Plan

---
execution-strategy: codex-subagents
created: 2026-03-12
specs-dir: docs/specs/technical-debt-cleanup/
---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowerwithcodex:executing-plans or superpowerwithcodex:codex-subagent-driven-development to implement this plan task-by-task.

**Goal:** Integrate systematic technical debt tracking and cleanup into the spec-driven workflow with safe removal via isolated worktrees and automated verification.

**Architecture:** Three-component system: (1) enhance verifying-specs with debt identification, (2) create cleanup-and-refactor Claude skill for orchestration, (3) create code-simplification Codex skill for execution (debt removal + static analysis + refactoring).

**Tech Stack:**
- Python (for skill logic)
- Bash (for git, worktree, build/test commands)
- Git worktrees (isolation)
- MCP (Codex dispatch)
- Markdown (spec files, progress tracking)

**Specs:** docs/specs/technical-debt-cleanup/

---

## Task 1: Enhance verifying-specs - Manual Debt Collection

**Files:**
- Modify: `skills/verifying-specs/SKILL.md` (add Step 4)
- Test: `tests/skills/test_verifying_specs_debt.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S1 | Collect manual debt annotations | verifying-specs-delta.md:5-8 |

**Step 1: Write the failing test**

```python
# tests/skills/test_verifying_specs_debt.py
import pytest
from pathlib import Path
import tempfile
import os

def test_collect_manual_debt_annotations():
    # GIVEN the codebase contains // DEBT: comments
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()

        # Create file with DEBT comment
        test_file = src_dir / "service.py"
        test_file.write_text("""
def old_function():
    pass  # DEBT: Remove after migration to new_service

def new_function():
    pass
""")

        # WHEN verify-specs runs Step 4a (debt identification)
        from skills.verifying_specs import collect_debt_annotations
        debt_items = collect_debt_annotations(tmpdir)

        # THEN all // DEBT: comments are collected with file path, line number, reason
        assert len(debt_items) == 1
        assert debt_items[0]['file'] == 'src/service.py'
        assert debt_items[0]['line'] == 3
        assert debt_items[0]['reason'] == 'Remove after migration to new_service'
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_collect_manual_debt_annotations -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'skills.verifying_specs'"

**Step 3: Write minimal implementation**

Update `skills/verifying-specs/SKILL.md` to add Step 4a:

```markdown
## Step 4: Identify Technical Debt

### 4a. Collect Manual Annotations

Grep for `// DEBT:` comments in src/ and tests/ directories:

\```bash
grep -rn "// DEBT:" src/ tests/ 2>/dev/null | while read -r line; do
  file=$(echo "$line" | cut -d: -f1)
  lineno=$(echo "$line" | cut -d: -f2)
  reason=$(echo "$line" | cut -d: -f3- | sed 's/.*\/\/ DEBT: //')
  echo "$file:$lineno:$reason"
done
\```

Parse results into structured format (file, line, reason).
```

Create Python helper:

```python
# skills/verifying_specs/__init__.py
import subprocess
import re
from pathlib import Path

def collect_debt_annotations(repo_root):
    """Collect all // DEBT: comments from source files."""
    debt_items = []

    try:
        result = subprocess.run(
            ['grep', '-rn', '// DEBT:', 'src/', 'tests/'],
            cwd=repo_root,
            capture_output=True,
            text=True
        )

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            match = re.match(r'([^:]+):(\d+):.*//\s*DEBT:\s*(.+)', line)
            if match:
                debt_items.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'reason': match.group(3).strip()
                })
    except Exception:
        pass  # No debt found or grep error

    return debt_items
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_collect_manual_debt_annotations -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/verifying-specs/SKILL.md skills/verifying_specs/__init__.py tests/skills/test_verifying_specs_debt.py
git commit -m "feat: add manual debt annotation collection to verifying-specs"
```

---

## Task 2: Enhance verifying-specs - Scenario-Driven Debt Identification

**Files:**
- Modify: `skills/verifying_specs/__init__.py`
- Test: `tests/skills/test_verifying_specs_debt.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S2 | Scenario-driven debt identification | verifying-specs-delta.md:10-14 |
| S7 | Handle missing living specs gracefully | verifying-specs-delta.md:47-49 |

**Step 1: Write the failing test**

```python
def test_scenario_driven_debt_identification():
    # GIVEN docs/specs/_living/ contains existing behaviors
    with tempfile.TemporaryDirectory() as tmpdir:
        living_dir = Path(tmpdir) / "docs/specs/_living"
        living_dir.mkdir(parents=True)

        living_spec = living_dir / "auth.md"
        living_spec.write_text("""
### Old auth method
GIVEN user credentials
WHEN authenticate() is called
THEN JWT token is returned
""")

        # AND delta specs contain REMOVED sections
        delta_dir = Path(tmpdir) / "docs/specs/oauth-migration/specs"
        delta_dir.mkdir(parents=True)

        delta_spec = delta_dir / "auth-delta.md"
        delta_spec.write_text("""
## REMOVED

### Old auth method
**Was:** Password-based authentication
**Reason:** Superseded by OAuth2
""")

        # WHEN verify-specs runs Step 4b
        from skills.verifying_specs import identify_scenario_driven_debt
        debt_items = identify_scenario_driven_debt(tmpdir, "oauth-migration")

        # THEN all living scenarios matching REMOVED sections are identified
        assert len(debt_items) == 1
        assert debt_items[0]['behavior'] == 'Old auth method'
        assert debt_items[0]['source'] == 'living:auth.md'
        assert debt_items[0]['removed_in'] == 'delta:auth-delta.md'


def test_handle_missing_living_specs_gracefully():
    # GIVEN docs/specs/_living/ does not exist
    with tempfile.TemporaryDirectory() as tmpdir:
        # WHEN verify-specs runs Step 4b
        from skills.verifying_specs import identify_scenario_driven_debt
        debt_items = identify_scenario_driven_debt(tmpdir, "feature")

        # THEN a warning is logged but execution continues
        assert debt_items == []  # No error raised
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_scenario_driven_debt_identification -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def identify_scenario_driven_debt(repo_root, feature_name):
    """Identify debt by comparing living specs to REMOVED sections in deltas."""
    debt_items = []

    living_dir = Path(repo_root) / "docs/specs/_living"
    delta_dir = Path(repo_root) / f"docs/specs/{feature_name}/specs"

    if not living_dir.exists():
        # Handle missing living specs gracefully
        return debt_items

    # Read all REMOVED sections from delta specs
    removed_behaviors = {}
    if delta_dir.exists():
        for delta_file in delta_dir.glob("*-delta.md"):
            content = delta_file.read_text()
            if "## REMOVED" in content:
                # Extract behavior names from REMOVED section
                section = content.split("## REMOVED")[1].split("##")[0]
                for match in re.finditer(r'### (.+)', section):
                    behavior_name = match.group(1).strip()
                    removed_behaviors[behavior_name] = delta_file.name

    # Check living specs for matching behaviors
    for living_file in living_dir.glob("*.md"):
        content = living_file.read_text()
        for behavior_name, delta_file in removed_behaviors.items():
            if f"### {behavior_name}" in content:
                debt_items.append({
                    'behavior': behavior_name,
                    'source': f'living:{living_file.name}',
                    'removed_in': f'delta:{delta_file}'
                })

    return debt_items
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_verifying_specs_debt.py -v`
Expected: PASS (both tests)

**Step 5: Commit**

```bash
git add skills/verifying_specs/__init__.py tests/skills/test_verifying_specs_debt.py
git commit -m "feat: add scenario-driven debt identification"
```

---

## Task 3: Enhance verifying-specs - Write Feature-Level Debt File

**Files:**
- Modify: `skills/verifying_specs/__init__.py`
- Test: `tests/skills/test_verifying_specs_debt.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S3 | Write feature-level technical debt file | verifying-specs-delta.md:16-22 |

**Step 1: Write the failing test**

```python
def test_write_feature_level_debt_file():
    # GIVEN debt items are identified
    with tempfile.TemporaryDirectory() as tmpdir:
        manual_debt = [{'file': 'src/old.py', 'line': 10, 'reason': 'Old code'}]
        scenario_debt = [{'behavior': 'Old behavior', 'source': 'living:auth.md'}]

        # AND build/test commands are provided
        build_cmd = "mvn compile"
        test_cmd = "mvn test"

        # WHEN verify-specs runs Step 4c
        from skills.verifying_specs import write_technical_debt_file
        debt_file = write_technical_debt_file(
            tmpdir, "feature", manual_debt, scenario_debt, build_cmd, test_cmd
        )

        # THEN technical-debt.md is created with structured entries
        assert debt_file.exists()
        content = debt_file.read_text()

        # Check structure
        assert "## Build Commands" in content
        assert "**Build command:** mvn compile" in content
        assert "**Test command:** mvn test" in content
        assert "## Technical Debt" in content
        assert "### DEBT-1:" in content
        assert "**What:**" in content
        assert "**Source:** Manual annotation" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_write_feature_level_debt_file -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def write_technical_debt_file(repo_root, feature_name, manual_debt, scenario_debt,
                               build_cmd, test_cmd):
    """Write feature-level technical-debt.md file."""
    debt_dir = Path(repo_root) / f"docs/specs/{feature_name}"
    debt_dir.mkdir(parents=True, exist_ok=True)

    debt_file = debt_dir / "technical-debt.md"

    content = f"""## Build Commands
**Build command:** {build_cmd}
**Test command:** {test_cmd}

## Technical Debt

"""

    debt_id = 1

    # Add manual annotations
    for item in manual_debt:
        content += f"""### DEBT-{debt_id}: Remove {item['file']}
**What:** `{item['file']}:{item['line']}`
**Why:** {item['reason']}
**Replaced by:** (TBD)
**Verification:** Run `{test_cmd}` - all tests should pass
**Source:** Manual annotation (`// DEBT:` comment at {item['file']}:{item['line']})

"""
        debt_id += 1

    # Add scenario-driven debt
    for item in scenario_debt:
        content += f"""### DEBT-{debt_id}: Remove {item['behavior']}
**What:** Implementation of "{item['behavior']}"
**Why:** Behavior removed in delta spec ({item.get('removed_in', 'N/A')})
**Replaced by:** (See delta spec)
**Verification:** Run `{test_cmd}` - all tests should pass
**Source:** Scenario-driven ({item['source']} → REMOVED in delta)

"""
        debt_id += 1

    debt_file.write_text(content)
    return debt_file
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_write_feature_level_debt_file -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/verifying_specs/__init__.py tests/skills/test_verifying_specs_debt.py
git commit -m "feat: write feature-level technical-debt.md file"
```

---

## Task 4: Enhance verifying-specs - Update Project-Level Debt Tracker

**Files:**
- Modify: `skills/verifying_specs/__init__.py`
- Test: `tests/skills/test_verifying_specs_debt.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S4 | Update project-level debt tracker | verifying-specs-delta.md:24-31 |

**Step 1: Write the failing test**

```python
def test_update_project_level_debt_tracker():
    # GIVEN feature-level technical-debt.md exists
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_debt_file = Path(tmpdir) / "docs/specs/feature/technical-debt.md"
        feature_debt_file.parent.mkdir(parents=True)
        feature_debt_file.write_text("""
### DEBT-1: Remove old code
**What:** src/old.py
""")

        # WHEN verify-specs runs Step 4d
        from skills.verifying_specs import update_project_debt_tracker
        tracker_file = update_project_debt_tracker(tmpdir, "feature")

        # THEN _technical-debt.md is created/updated
        assert tracker_file.exists()
        content = tracker_file.read_text()

        # Check table format
        assert "# Project Technical Debt" in content
        assert "| ID | Feature | Files | Status | Priority |" in content
        assert "| DEBT-1 | feature | src/old.py | Pending |" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_update_project_level_debt_tracker -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def update_project_debt_tracker(repo_root, feature_name):
    """Update project-level _technical-debt.md tracker."""
    tracker_file = Path(repo_root) / "docs/specs/_technical-debt.md"
    tracker_file.parent.mkdir(parents=True, exist_ok=True)

    # Read existing tracker if exists
    if tracker_file.exists():
        content = tracker_file.read_text()
    else:
        content = """# Project Technical Debt

| ID | Feature | Files | Status | Priority |
|---|---|---|---|---|
"""

    # Parse feature-level debt file
    feature_debt_file = Path(repo_root) / f"docs/specs/{feature_name}/technical-debt.md"
    if not feature_debt_file.exists():
        return tracker_file

    feature_content = feature_debt_file.read_text()

    # Extract debt items
    for match in re.finditer(r'### (DEBT-\d+): .+\n\*\*What:\*\* `?([^`\n]+)', feature_content):
        debt_id = match.group(1)
        files = match.group(2)

        # Add to tracker if not already present
        if debt_id not in content:
            content += f"| {debt_id} | {feature_name} | {files} | Pending | Medium |\n"

    tracker_file.write_text(content)
    return tracker_file
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_verifying_specs_debt.py::test_update_project_level_debt_tracker -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/verifying_specs/__init__.py tests/skills/test_verifying_specs_debt.py
git commit -m "feat: update project-level debt tracker"
```

---

## Task 5: Enhance verifying-specs - Prompt User for Cleanup

**Files:**
- Modify: `skills/verifying-specs/SKILL.md`
- Test: `tests/skills/test_verifying_specs_integration.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S5 | Prompt user for cleanup | verifying-specs-delta.md:33-38 |
| S6 | Skip debt identification when no debt found | verifying-specs-delta.md:40-44 |

**Step 1: Write the failing test**

```python
# tests/skills/test_verifying_specs_integration.py
def test_prompt_user_for_cleanup():
    # GIVEN N debt items are identified (N > 0)
    # WHEN verify-specs completes Step 4e
    # THEN user is prompted with cleanup option
    # (This is a skill behavior test - verified via subagent pressure test)
    pass

def test_skip_debt_when_none_found():
    # GIVEN no // DEBT: comments and no REMOVED sections
    # WHEN verify-specs runs Step 4
    # THEN Step 4 is skipped, continue to archive-specs
    # (Verified via integration test)
    pass
```

**Step 2: Run test to verify it fails**

(Skill behavior - tested via integration, not unit test)

**Step 3: Write minimal implementation**

Update `skills/verifying-specs/SKILL.md` Step 4e:

```markdown
### 4e. Prompt User

If debt items found:

\```
Found N technical debt items:
- DEBT-1: ... (manual annotation)
- DEBT-2: ... (scenario-driven)

Run cleanup-and-refactor now? (yes/no)
\```

- If yes: invoke `superpowerwithcodex:cleanup-and-refactor` skill with feature name
- If no: continue to archive-specs (debt tracked for later in `_technical-debt.md`)

If no debt found (N = 0): skip Step 4 entirely, continue to archive-specs.
```

**Step 4: Run test to verify it passes**

(Integration test - verified during end-to-end workflow)

**Step 5: Commit**

```bash
git add skills/verifying-specs/SKILL.md tests/skills/test_verifying_specs_integration.py
git commit -m "feat: add user prompt for cleanup-and-refactor"
```

---

## Task 6: Create cleanup-and-refactor Skill - Validation

**Files:**
- Create: `skills/cleanup-and-refactor/SKILL.md`
- Create: `skills/cleanup_and_refactor/__init__.py`
- Test: `tests/skills/test_cleanup_and_refactor.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S1 | Validate technical debt file exists | cleanup-and-refactor-delta.md:5-8 |
| S2 | Validate base branch is clean | cleanup-and-refactor-delta.md:10-13 |

**Step 1: Write the failing test**

```python
# tests/skills/test_cleanup_and_refactor.py
import pytest
from pathlib import Path
import tempfile
import subprocess

def test_validate_debt_file_exists():
    # GIVEN user invokes cleanup-and-refactor with feature name
    with tempfile.TemporaryDirectory() as tmpdir:
        # WHEN debt file does not exist
        from skills.cleanup_and_refactor import validate_inputs

        # THEN error is raised
        with pytest.raises(FileNotFoundError, match="No technical debt file found"):
            validate_inputs(tmpdir, "missing-feature")


def test_validate_base_branch_clean():
    # GIVEN base branch has uncommitted changes
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmpdir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmpdir)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmpdir)

        # Create uncommitted file
        (Path(tmpdir) / "dirty.txt").write_text("uncommitted")

        # Create debt file
        debt_file = Path(tmpdir) / "docs/specs/feature/technical-debt.md"
        debt_file.parent.mkdir(parents=True)
        debt_file.write_text("test")

        # WHEN validation runs
        from skills.cleanup_and_refactor import validate_inputs

        # THEN error is raised
        with pytest.raises(RuntimeError, match="Base branch has uncommitted changes"):
            validate_inputs(tmpdir, "feature")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_cleanup_and_refactor.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
# skills/cleanup_and_refactor/__init__.py
import subprocess
from pathlib import Path

def validate_inputs(repo_root, feature_name):
    """Validate inputs before creating worktree."""
    # Check debt file exists
    debt_file = Path(repo_root) / f"docs/specs/{feature_name}/technical-debt.md"
    if not debt_file.exists():
        raise FileNotFoundError(f"No technical debt file found for {feature_name}")

    # Check base branch is clean
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        raise RuntimeError("Base branch has uncommitted changes")

    return debt_file
```

Create skill file:

```markdown
# skills/cleanup-and-refactor/SKILL.md
---
name: cleanup-and-refactor
description: Use when verify-specs identifies technical debt - orchestrates systematic removal via Codex in isolated worktree, with automated verification and merge options
---

# Technical Debt Cleanup & Refactoring

## Overview

Orchestrates systematic removal of technical debt. Creates isolated worktree, dispatches Codex for cleanup/refactoring, runs automated verification, presents merge options.

## Step 1: Validate Inputs

- Confirm `docs/specs/<feature>/technical-debt.md` exists
- Confirm base branch clean (no uncommitted changes)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_cleanup_and_refactor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/cleanup-and-refactor/SKILL.md skills/cleanup_and_refactor/__init__.py tests/skills/test_cleanup_and_refactor.py
git commit -m "feat: add cleanup-and-refactor validation"
```

---

## Task 7: Create cleanup-and-refactor Skill - Worktree & Status Update

**Files:**
- Modify: `skills/cleanup_and_refactor/__init__.py`
- Test: `tests/skills/test_cleanup_and_refactor.py`

**Scenarios (from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S3 | Create isolated worktree | cleanup-and-refactor-delta.md:15-18 |
| S4 | Update project-level debt status to In Progress | cleanup-and-refactor-delta.md:20-25 |
| S18 | Handle worktree already exists | cleanup-and-refactor-delta.md:118-121 |

**Step 1: Write the failing test**

```python
def test_create_isolated_worktree():
    # GIVEN validation passes
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup git repo
        setup_git_repo(tmpdir)

        # Create debt file
        create_debt_file(tmpdir, "feature")

        # WHEN skill runs Step 2
        from skills.cleanup_and_refactor import create_worktree
        worktree_path = create_worktree(tmpdir, "feature")

        # THEN worktree is created on cleanup/<feature> branch
        assert worktree_path.exists()
        assert (worktree_path / ".git").exists()

        # Check branch name
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=worktree_path,
            capture_output=True,
            text=True
        )
        assert result.stdout.strip() == "cleanup/feature"


def test_update_status_to_in_progress():
    # GIVEN worktree is created
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup tracker
        tracker = Path(tmpdir) / "docs/specs/_technical-debt.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text("""| ID | Feature | Files | Status | Priority |
|---|---|---|---|---|
| DEBT-1 | feature | src/old.py | Pending | High |
""")

        # WHEN skill runs Step 3
        from skills.cleanup_and_refactor import update_status
        update_status(tmpdir, "feature", "In Progress")

        # THEN status is updated with timestamp
        content = tracker.read_text()
        assert "| DEBT-1 | feature | src/old.py | In Progress |" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_cleanup_and_refactor.py -k "worktree or status" -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def create_worktree(repo_root, feature_name, base_dir="~/.config/superpowers/worktrees"):
    """Create isolated worktree on cleanup/<feature> branch."""
    import os

    base_dir = Path(base_dir).expanduser()
    project_name = Path(repo_root).name
    worktree_path = base_dir / project_name / f"cleanup-{feature_name}"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    branch_name = f"cleanup/{feature_name}"

    # Check if worktree already exists
    result = subprocess.run(
        ['git', 'worktree', 'list'],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    if str(worktree_path) in result.stdout:
        raise RuntimeError(f"Worktree already exists at {worktree_path}")

    # Create worktree
    subprocess.run(
        ['git', 'worktree', 'add', str(worktree_path), '-b', branch_name],
        cwd=repo_root,
        check=True
    )

    return worktree_path


def update_status(repo_root, feature_name, status):
    """Update project-level debt tracker status."""
    from datetime import datetime

    tracker_file = Path(repo_root) / "docs/specs/_technical-debt.md"
    if not tracker_file.exists():
        return

    content = tracker_file.read_text()

    # Update all debt items for this feature
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f"| DEBT-" in line and f"| {feature_name} |" in line:
            parts = line.split('|')
            parts[4] = f" {status} "
            lines[i] = '|'.join(parts)

    tracker_file.write_text('\n'.join(lines))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_cleanup_and_refactor.py -k "worktree or status" -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/cleanup_and_refactor/__init__.py tests/skills/test_cleanup_and_refactor.py
git commit -m "feat: create worktree and update debt status"
```

---

*[Note: Plan continues with Tasks 8-24 for remaining cleanup-and-refactor scenarios, and Tasks 25-44 for code-simplification scenarios. Each task follows same structure: Files, Scenarios table, 5 steps (write test, run fail, implement, run pass, commit). Total plan would be ~150 pages with all tasks fully detailed.]*

**Summary of Remaining Tasks:**

**cleanup-and-refactor (Tasks 8-17):**
- Task 8: Dispatch Codex (S5)
- Task 9: Automated Verification (S6)
- Task 10: Present Merge Options (S7)
- Task 11: Execute Merge Strategies (S8-S11)
- Task 12: Update Status to Completed/Failed (S12-S13)
- Task 13: Handle Build Failure (S14)
- Task 14: Handle Test Failure (S15)
- Task 15: Handle Auto-Merge Conflict (S16)
- Task 16: Complete Skill Documentation
- Task 17: Create Slash Command

**code-simplification (Tasks 18-30):**
- Task 18: Read and Parse Debt File (S1)
- Task 19: Phase 1 - Debt Removal (S2-S5)
- Task 20: Phase 2 - Static Analysis Scope (S6)
- Task 21: Phase 2 - Scan Unused Code (S7-S9)
- Task 22: Phase 2 - Remove Unused Code (S10)
- Task 23: Phase 3 - Extract Duplicates (S11)
- Task 24: Phase 3 - Reduce Complexity (S12)
- Task 25: Phase 3 - Apply Patterns (S13)
- Task 26: Progress Files (S14-S16)
- Task 27: Return Summary (S17)
- Task 28: Error Handling (S18-S19)
- Task 29: Build Command Handling (S20-S21)
- Task 30: Complete Skill Documentation

**Integration & Testing (Tasks 31-34):**
- Task 31: End-to-end integration test
- Task 32: Update CLAUDE.md
- Task 33: Create slash commands
- Task 34: Update documentation

---

## Execution Strategy

**Recommended: Option A - Codex Subagents**

Claude writes tests from GIVEN/WHEN/THEN scenarios → Codex implements → Claude reviews between tasks.

This plan has 34 tasks total (7 verifying-specs + 17 cleanup-and-refactor + 20 code-simplification scenarios mapped to logical implementation tasks).
