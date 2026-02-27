"""Test 10: Verify CLAUDE.md was updated with all new skills and workflow changes."""

import os

import pytest

from conftest import REPO_ROOT


@pytest.fixture
def claude_md():
    path = os.path.join(REPO_ROOT, "CLAUDE.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestClaudeMdNewCommands:
    """CLAUDE.md must document all 3 new slash commands."""

    @pytest.mark.parametrize("command", ["write-specs", "verify-specs", "archive-specs"])
    def test_command_documented(self, claude_md, command):
        assert command in claude_md, (
            f"CLAUDE.md missing documentation for /{command} command"
        )


class TestClaudeMdWorkflowCycle:
    """The Superpowers Cycle must include the new spec steps."""

    def test_has_writing_specs_step(self, claude_md):
        assert "writing-specs" in claude_md or "write-specs" in claude_md

    def test_has_verifying_specs_step(self, claude_md):
        assert "verifying-specs" in claude_md or "verify-specs" in claude_md

    def test_has_archiving_specs_step(self, claude_md):
        assert "archiving-specs" in claude_md or "archive-specs" in claude_md


class TestClaudeMdStructuredSpecsSection:
    """CLAUDE.md must have a full Structured Specifications documentation section."""

    def test_has_structured_specs_section(self, claude_md):
        assert "Structured Specifications" in claude_md

    def test_has_directory_convention(self, claude_md):
        assert "Directory Convention" in claude_md or "directory convention" in claude_md.lower()

    def test_has_delta_spec_format(self, claude_md):
        assert "Delta Spec" in claude_md or "delta spec" in claude_md.lower()

    def test_has_workflow_documentation(self, claude_md):
        assert "Write specs" in claude_md or "write-specs" in claude_md
        assert "Verify" in claude_md
        assert "Archive" in claude_md


class TestClaudeMdImportantFiles:
    """Important Files section must include new skill files."""

    @pytest.mark.parametrize("skill_file", [
        "skills/writing-specs/SKILL.md",
        "skills/verifying-specs/SKILL.md",
        "skills/archiving-specs/SKILL.md",
    ])
    def test_skill_in_important_files(self, claude_md, skill_file):
        assert skill_file in claude_md, (
            f"CLAUDE.md Important Files section missing {skill_file}"
        )
