"""Mini-spec format validation for LIGHT feature directories."""

import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT


VALID_MINI_SPEC = """---
mode: light
feature: sample-light
date: 2026-07-04
---

# Sample Light - Mini Spec

Intent: Keep a small change covered by scenarios.

## Scenarios

### First Behavior
GIVEN a valid mini-spec
WHEN validate_specs.py runs
THEN the directory passes without full-layout files

### Second Behavior
GIVEN the mini-spec has enough scenarios
WHEN validate_specs.py counts scenarios
THEN the allowed range is satisfied

## Out of Scope
- Full proposal and design files
"""


def run_validator(feature_dir: Path):
    return subprocess.run(
        [sys.executable, str(Path(REPO_ROOT) / "scripts" / "validate_specs.py"), str(feature_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_mini(feature_dir: Path, content: str = VALID_MINI_SPEC):
    feature_dir.mkdir(parents=True)
    (feature_dir / "mini.md").write_text(content, encoding="utf-8")


class TestMiniSpecValidation:
    def test_valid_mini_spec_directory_does_not_require_full_layout(self, tmp_path):
        feature_dir = tmp_path / "docs" / "specs" / "sample-light"
        write_mini(feature_dir)

        result = run_validator(feature_dir)

        assert result.returncode == 0, result.stderr + result.stdout
        assert "OK: mini spec, 2 scenario(s)" in result.stdout

    def test_missing_light_mode_is_rejected(self, tmp_path):
        feature_dir = tmp_path / "docs" / "specs" / "missing-mode"
        write_mini(feature_dir, VALID_MINI_SPEC.replace("mode: light\n", ""))

        result = run_validator(feature_dir)

        assert result.returncode == 1
        assert "mode: light" in result.stdout
        assert "frontmatter" in result.stdout

    def test_scenario_count_below_bounds_is_rejected(self, tmp_path):
        feature_dir = tmp_path / "docs" / "specs" / "too-few"
        write_mini(
            feature_dir,
            """---
mode: light
---

# Too Few - Mini Spec

Intent: Missing the required second scenario.

## Scenarios

### Only Behavior
GIVEN one scenario
WHEN validate_specs.py counts scenarios
THEN it rejects the mini-spec

## Out of Scope
- Extra scenarios
""",
        )

        result = run_validator(feature_dir)

        assert result.returncode == 1
        assert "scenario count 1" in result.stdout
        assert "allowed range is 2-5" in result.stdout

    def test_scenario_count_above_bounds_is_rejected(self, tmp_path):
        feature_dir = tmp_path / "docs" / "specs" / "too-many"
        scenarios = "\n\n".join(
            [
                f"""### Behavior {index}
GIVEN scenario {index}
WHEN validate_specs.py counts scenarios
THEN it includes scenario {index}"""
                for index in range(1, 7)
            ]
        )
        write_mini(
            feature_dir,
            f"""---
mode: light
---

# Too Many - Mini Spec

Intent: Has too many scenarios.

## Scenarios

{scenarios}

## Out of Scope
- None
""",
        )

        result = run_validator(feature_dir)

        assert result.returncode == 1
        assert "scenario count 6" in result.stdout
        assert "allowed range is 2-5" in result.stdout

    def test_mixing_mini_and_delta_specs_is_rejected(self, tmp_path):
        feature_dir = tmp_path / "docs" / "specs" / "mixed"
        write_mini(feature_dir)
        specs_dir = feature_dir / "specs"
        specs_dir.mkdir()
        (specs_dir / "mixed-delta.md").write_text(
            """# Mixed Delta

## ADDED

### Delta Behavior
GIVEN a mixed feature directory
WHEN validate_specs.py runs
THEN it rejects ambiguous spec modes
""",
            encoding="utf-8",
        )

        result = run_validator(feature_dir)

        assert result.returncode == 1
        assert "either LIGHT (mini.md) or FULL (proposal/design/deltas), not both" in result.stdout
