"""Verify the handover-manager spec contract."""

import json
import os
import subprocess

from conftest import REPO_ROOT, SKILLS_DIR, _extract_frontmatter, _read_skill


HANDOVER_SKILL = "handover-manager"


class TestHandoverManagerSkillFile:
    """The handover-manager skill must exist with valid frontmatter."""

    def test_skill_file_exists(self):
        path = os.path.join(SKILLS_DIR, HANDOVER_SKILL, "SKILL.md")
        assert os.path.isfile(path)

    def test_frontmatter_shape(self):
        content = _read_skill(HANDOVER_SKILL)
        frontmatter = _extract_frontmatter(content)

        assert frontmatter == {
            "name": HANDOVER_SKILL,
            "description": frontmatter.get("description"),
        }
        assert frontmatter["description"].startswith("Use when")
        assert len(frontmatter["name"]) + len(frontmatter["description"]) <= 1024


class TestHandoverDocumentGenerationRules:
    """Skill text encodes the deterministic handover generation contract."""

    def test_contains_required_handover_sections(self):
        content = _read_skill(HANDOVER_SKILL)

        assert "docs/handovers/YYYY-MM-DD-HHmm-<topic>.md" in content
        for section in (
            "## Decisions",
            "## Changes this round",
            "## File list",
            "## Verification results",
            "## Open items",
            "## Restart instructions",
        ):
            assert section in content

    def test_requires_git_verified_file_list(self):
        content = _read_skill(HANDOVER_SKILL)

        assert "git diff --stat" in content
        assert "git status" in content
        assert "not list files from memory" in content

    def test_handles_non_git_directories(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "not a git repository" in lower or "git verification was unavailable" in lower
        assert "instead of listing files from memory" in lower

    def test_updates_latest_index_with_topic_and_status(self):
        content = _read_skill(HANDOVER_SKILL)

        assert "docs/handovers/LATEST.md" in content
        assert "topic" in content.lower()
        assert "status" in content.lower()
        assert "rewritten" in content.lower() or "rewrite" in content.lower()

    def test_requires_honest_verification_results(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "actual test command" in lower
        assert "real output summary" in lower
        assert "failures" in lower
        assert "without claiming more progress than occurred" in lower

    def test_requires_executable_restart_instructions(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "copy-pasteable command" in lower
        assert "file path" in lower
        assert "vague description" in lower

    def test_references_fine_grained_ledgers_instead_of_copying(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "progress.md" in content
        assert "ledger" in lower
        assert "rather than duplicating" in lower or "instead of copying" in lower


class TestHandoverTriggersAndResumeRules:
    """Skill text covers trigger and resume scenarios."""

    def test_has_tool_switch_trigger(self):
        content = _read_skill(HANDOVER_SKILL)

        assert "Codex" in content
        assert "Claude Cowork" in content
        assert "another session" in content
        assert "before the switch" in content

    def test_resume_reads_latest_and_does_not_reask_settled_decisions(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "docs/handovers/LATEST.md" in content
        assert "restore" in lower
        assert "open items" in lower
        assert "restart instructions" in lower
        assert "does not re-ask settled decisions" in lower

    def test_resume_repairs_broken_latest_index(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "missing file" in lower or "does not exist" in lower
        assert "newest timestamped file" in lower
        assert "repair" in lower

    def test_resume_without_handover_does_not_fabricate_prior_state(self):
        content = _read_skill(HANDOVER_SKILL)
        lower = content.lower()

        assert "no handover" in lower
        assert "normal context gathering" in lower
        assert "without fabricating prior state" in lower


class TestFinishingBranchHandoverIntegration:
    """Finishing a branch must hand off before presenting final options."""

    def test_finishing_branch_writes_done_handover_before_options(self):
        content = _read_skill("finishing-a-development-branch")

        handover_index = content.index("handover-manager")
        options_index = content.index("Present Options")

        assert handover_index < options_index
        assert "status" in content[handover_index:options_index].lower()
        assert "done" in content[handover_index:options_index].lower()

    def test_finishing_branch_spec_success_routes_to_handover_step(self):
        content = _read_skill("finishing-a-development-branch")

        assert "If verification **passes:** Continue to Step 1c." in content
        assert "If no specs directory exists: Skip to Step 1c." in content


class TestPreCompactHook:
    """The PreCompact hook is registered and emits valid non-blocking JSON."""

    def test_precompact_hook_registered_through_run_hook(self):
        hooks_path = os.path.join(REPO_ROOT, "hooks", "hooks.json")
        with open(hooks_path, "r", encoding="utf-8") as handle:
            hooks = json.load(handle)["hooks"]

        assert "PreCompact" in hooks
        commands = [
            hook["command"]
            for entry in hooks["PreCompact"]
            for hook in entry["hooks"]
            if hook["type"] == "command"
        ]
        assert any("run-hook.cmd" in command and "pre-compact.sh" in command for command in commands)

    def test_precompact_hook_outputs_single_valid_json_object(self):
        script_path = os.path.join(REPO_ROOT, "hooks", "pre-compact.sh")

        result = subprocess.run(
            ["bash", script_path],
            check=False,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0
        assert result.stderr == ""

        output = result.stdout.strip()
        assert output.startswith("{")
        assert output.endswith("}")
        assert output.count("{") >= 2

        payload = json.loads(output)
        hook_output = payload["hookSpecificOutput"]
        assert hook_output["hookEventName"] == "PreCompact"
        reminder = hook_output["additionalContext"]
        assert "handover-manager" in reminder
        assert "docs/handovers/YYYY-MM-DD-HHmm-<topic>.md" in reminder
        assert "before compaction" in reminder.lower()
