import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_specs.py"


def run_validator(feature_dir):
    return run_validator_args(str(feature_dir))


def run_validator_args(*args):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_valid_feature(tmp_path):
    feature_dir = tmp_path / "feature"
    specs_dir = feature_dir / "specs"
    specs_dir.mkdir(parents=True)
    (feature_dir / "proposal.md").write_text(
        """# Test Proposal

## Intent

Validate useful intent.

## Scope

Validate useful scope.
""",
        encoding="utf-8",
    )
    (feature_dir / "design.md").write_text("# Design\n\nUseful design.\n", encoding="utf-8")
    (specs_dir / "test-delta.md").write_text(
        """# Test Delta

## ADDED

### Valid Behavior
GIVEN a valid precondition
WHEN the action runs
THEN the expected result occurs
""",
        encoding="utf-8",
    )
    return feature_dir


def stdout_lines(result):
    return result.stdout.strip().splitlines()


def test_valid_feature_directory_exits_zero_and_reports_counts(tmp_path):
    feature_dir = write_valid_feature(tmp_path)

    result = run_validator(feature_dir)

    assert result.returncode == 0
    assert stdout_lines(result) == ["OK: 1 delta spec(s), 1 scenario(s)"]
    assert result.stderr == ""


def test_missing_proposal_exits_one_and_names_missing_file(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    (feature_dir / "proposal.md").unlink()

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "proposal.md" in result.stdout
    assert "missing" in result.stdout


def test_empty_intent_section_exits_one_and_names_section(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    (feature_dir / "proposal.md").write_text(
        """# Test Proposal

## Intent

## Scope

Validate useful scope.
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "proposal.md" in result.stdout
    assert "Intent" in result.stdout
    assert "empty" in result.stdout


def test_missing_design_exits_one_and_names_missing_file(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    (feature_dir / "design.md").unlink()

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "design.md" in result.stdout
    assert "missing" in result.stdout


def test_missing_or_empty_specs_directory_exits_one(tmp_path):
    missing_specs = write_valid_feature(tmp_path / "missing")
    empty_specs = write_valid_feature(tmp_path / "empty")
    for delta_file in (empty_specs / "specs").glob("*-delta.md"):
        delta_file.unlink()
    for child in (missing_specs / "specs").iterdir():
        child.unlink()
    (missing_specs / "specs").rmdir()

    missing_result = run_validator(missing_specs)
    empty_result = run_validator(empty_specs)

    for result in (missing_result, empty_result):
        assert result.returncode == 1
        assert "ERROR" in result.stdout
        assert "no delta specs were found" in result.stdout


def test_delta_file_without_change_sections_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

### Orphan Behavior
GIVEN a precondition
WHEN an action runs
THEN a result occurs
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "test-delta.md" in result.stdout
    assert "no change sections" in result.stdout


def test_added_behavior_without_complete_scenario_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## ADDED

### Incomplete Behavior
GIVEN a precondition exists
WHEN the action runs
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "test-delta.md" in result.stdout
    assert "Incomplete Behavior" in result.stdout
    assert "scenario is incomplete" in result.stdout


def test_single_line_added_scenario_counts_as_complete(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## ADDED

### Single Line Behavior
GIVEN x WHEN y THEN z
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 0
    assert stdout_lines(result) == ["OK: 1 delta spec(s), 1 scenario(s)"]


def test_all_violations_are_reported_in_one_run(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    (feature_dir / "design.md").unlink()
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## ADDED

### Incomplete Behavior
GIVEN a precondition exists
WHEN the action runs
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    lines = stdout_lines(result)
    assert any("design.md" in line and "missing" in line for line in lines)
    assert any("Incomplete Behavior" in line and "scenario is incomplete" in line for line in lines)


def test_modified_behavior_missing_reason_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## MODIFIED

### Changed Behavior
**Was:** Old behavior
**Now:** New behavior

GIVEN a precondition
WHEN an action runs
THEN a result occurs
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "Changed Behavior" in result.stdout
    assert "Reason" in result.stdout


def test_modified_behavior_missing_scenario_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## MODIFIED

### Changed Behavior
**Was:** Old behavior
**Now:** New behavior
**Reason:** Better behavior
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "Changed Behavior" in result.stdout
    assert "scenario is incomplete" in result.stdout


def test_removed_behavior_missing_was_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## REMOVED

### Removed Behavior
**Reason:** No longer needed
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "Removed Behavior" in result.stdout
    assert "Was" in result.stdout


def test_behavior_in_both_modified_and_removed_exits_one(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    delta_file = feature_dir / "specs" / "test-delta.md"
    delta_file.write_text(
        """# Test Delta

## MODIFIED

### Shared Behavior
**Was:** Old behavior
**Now:** New behavior
**Reason:** Better behavior

GIVEN a precondition
WHEN an action runs
THEN a result occurs

## REMOVED

###  shared behavior  
**Was:** Old behavior
**Reason:** No longer needed
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 1
    assert "ERROR" in result.stdout
    assert "Shared Behavior" in result.stdout or "shared behavior" in result.stdout
    assert "appears in both MODIFIED and REMOVED" in result.stdout


def test_usage_errors_exit_two_and_print_usage_to_stderr(tmp_path):
    missing_arg = run_validator_args()
    nonexistent = run_validator(tmp_path / "does-not-exist")
    living_dir = write_valid_feature(tmp_path / "living")
    archive_dir = write_valid_feature(tmp_path / "archive")
    living_target = tmp_path / "feature_living"
    archive_target = tmp_path / "feature_archive"
    living_dir.rename(living_target)
    archive_dir.rename(archive_target)

    for result in (
        missing_arg,
        nonexistent,
        run_validator(living_target),
        run_validator(archive_target),
    ):
        assert result.returncode == 2
        assert result.stdout == ""
        assert "Usage:" in result.stderr


def test_non_delta_files_in_specs_directory_are_ignored_and_not_counted(tmp_path):
    feature_dir = write_valid_feature(tmp_path)
    (feature_dir / "specs" / "notes.md").write_text(
        """# Notes

## ADDED

### Invalid Note Behavior
GIVEN this note is not a delta spec
""",
        encoding="utf-8",
    )

    result = run_validator(feature_dir)

    assert result.returncode == 0
    assert stdout_lines(result) == ["OK: 1 delta spec(s), 1 scenario(s)"]
    assert "notes.md" not in result.stdout
