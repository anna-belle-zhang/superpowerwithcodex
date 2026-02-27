"""Test 2: Verify slash command files exist and route to correct skills."""

import os

import pytest

from conftest import COMMANDS_DIR, _extract_frontmatter, _read_command


COMMANDS = {
    "write-specs": "writing-specs",
    "verify-specs": "verifying-specs",
    "archive-specs": "archiving-specs",
}


class TestCommandFileExistence:
    """All three new command files must exist."""

    @pytest.mark.parametrize("command_name", COMMANDS.keys())
    def test_command_file_exists(self, command_name):
        cmd_file = os.path.join(COMMANDS_DIR, f"{command_name}.md")
        assert os.path.isfile(cmd_file), f"Command file missing: {cmd_file}"


class TestCommandFrontmatter:
    """Command files must have description in frontmatter."""

    @pytest.mark.parametrize("command_name", COMMANDS.keys())
    def test_has_description(self, command_name):
        content = _read_command(command_name)
        fm = _extract_frontmatter(content)
        assert fm.get("description"), (
            f"{command_name} command missing 'description' in frontmatter"
        )


class TestCommandRouting:
    """Commands must reference the correct skill."""

    @pytest.mark.parametrize("command_name,skill_name", COMMANDS.items())
    def test_routes_to_correct_skill(self, command_name, skill_name):
        content = _read_command(command_name)
        assert skill_name in content, (
            f"Command '{command_name}' does not reference skill '{skill_name}'"
        )

    @pytest.mark.parametrize("command_name", COMMANDS.keys())
    def test_instructs_to_follow_skill(self, command_name):
        content = _read_command(command_name)
        lower = content.lower()
        assert "follow" in lower or "use" in lower, (
            f"Command '{command_name}' doesn't instruct to follow/use the skill"
        )
