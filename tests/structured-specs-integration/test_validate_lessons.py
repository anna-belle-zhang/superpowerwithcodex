"""Lessons file format validation for learn skill artifacts."""

import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT


VALID_LESSONS = """# Lessons

## [tag: codex-sandbox-network] Codex Sandbox Network
- Symptom: Network calls fail unexpectedly inside Codex.
- Root cause: The sandbox blocks network access unless configured.
- Correct approach: Treat network as unavailable unless the environment says otherwise.
- Occurrences: 2026-07-03 (project-a), 2026-07-04 (project-b)
- Level: pattern
"""


def run_validator(path: Path):
    return subprocess.run(
        [sys.executable, str(Path(REPO_ROOT) / "scripts" / "validate_lessons.py"), str(path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_lessons(tmp_path: Path, content: str = VALID_LESSONS) -> Path:
    path = tmp_path / "docs" / "lessons.md"
    path.parent.mkdir(parents=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestValidateLessonsFormat:
    def test_accepts_well_formed_lessons_file(self, tmp_path):
        path = write_lessons(tmp_path)

        result = run_validator(path)

        assert result.returncode == 0, result.stderr + result.stdout
        assert "OK: 1 lesson entry(s)" in result.stdout

    def test_missing_file_is_not_an_error(self, tmp_path):
        path = tmp_path / "docs" / "lessons.md"

        result = run_validator(path)

        assert result.returncode == 0
        assert "OK: lessons file not found" in result.stdout

    def test_rejects_missing_required_field_and_names_tag(self, tmp_path):
        path = write_lessons(
            tmp_path,
            VALID_LESSONS.replace("- Root cause: The sandbox blocks network access unless configured.\n", ""),
        )

        result = run_validator(path)

        assert result.returncode == 1
        assert "codex-sandbox-network" in result.stdout
        assert "missing required field: Root cause" in result.stdout

    def test_rejects_heading_without_tag_key(self, tmp_path):
        path = write_lessons(tmp_path, VALID_LESSONS.replace("[tag: codex-sandbox-network] ", ""))

        result = run_validator(path)

        assert result.returncode == 1
        assert "Codex Sandbox Network" in result.stdout
        assert "heading must include [tag: <kebab-case-tag>]" in result.stdout

    def test_rejects_empty_tag(self, tmp_path):
        path = write_lessons(tmp_path, VALID_LESSONS.replace("[tag: codex-sandbox-network]", "[tag: ]"))

        result = run_validator(path)

        assert result.returncode == 1
        assert "[tag: ] Codex Sandbox Network" in result.stdout
        assert "heading must include [tag: <kebab-case-tag>]" in result.stdout

    def test_rejects_invalid_level_and_names_allowed_values(self, tmp_path):
        path = write_lessons(tmp_path, VALID_LESSONS.replace("- Level: pattern", "- Level: habit"))

        result = run_validator(path)

        assert result.returncode == 1
        assert "codex-sandbox-network" in result.stdout
        assert "Level must be one of: lesson, pattern" in result.stdout

    def test_rejects_duplicate_tags(self, tmp_path):
        second = VALID_LESSONS.replace("Codex Sandbox Network", "Repeated Sandbox Lesson")
        path = write_lessons(tmp_path, VALID_LESSONS + "\n" + second)

        result = run_validator(path)

        assert result.returncode == 1
        assert "duplicate tag: codex-sandbox-network" in result.stdout
        assert "Occurrences line" in result.stdout

    def test_flags_pattern_level_with_too_few_occurrences(self, tmp_path):
        path = write_lessons(
            tmp_path,
            VALID_LESSONS.replace(
                "2026-07-03 (project-a), 2026-07-04 (project-b)",
                "2026-07-03 (project-a)",
            ),
        )

        result = run_validator(path)

        assert result.returncode == 1
        assert "codex-sandbox-network" in result.stdout
        assert "pattern level requires at least 2 occurrences" in result.stdout

    def test_rejects_undated_occurrence_with_named_error(self, tmp_path):
        path = write_lessons(
            tmp_path,
            VALID_LESSONS.replace(
                "2026-07-03 (project-a), 2026-07-04 (project-b)",
                "project-a, 2026-07-04 (project-b)",
            ),
        )

        result = run_validator(path)

        assert result.returncode == 1
        assert "codex-sandbox-network" in result.stdout
        assert "occurrence missing YYYY-MM-DD date" in result.stdout
