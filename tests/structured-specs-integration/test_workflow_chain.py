"""Test 9: Verify the full workflow chain is correctly wired across skills."""

from conftest import _read_skill


class TestWorkflowChainWiring:
    """Skills must reference each other in the correct order per the enhanced workflow:
    brainstorm -> write-specs -> worktree -> write-plan -> execute -> verify-specs -> archive-specs -> finish
    """

    def test_brainstorming_triggers_write_specs(self):
        content = _read_skill("brainstorming")
        assert "write-specs" in content

    def test_writing_specs_consumed_by_writing_plans(self):
        content = _read_skill("writing-specs")
        assert "writing-plans" in content

    def test_writing_specs_consumed_by_codex(self):
        content = _read_skill("writing-specs")
        assert "codex-subagent" in content.lower() or "codex" in content.lower()

    def test_writing_specs_consumed_by_verify(self):
        content = _read_skill("writing-specs")
        assert "verifying-specs" in content

    def test_writing_specs_consumed_by_archive(self):
        content = _read_skill("writing-specs")
        assert "archiving-specs" in content

    def test_verifying_specs_called_by_finishing(self):
        content = _read_skill("verifying-specs")
        assert "finishing" in content.lower()

    def test_verifying_specs_followed_by_archiving(self):
        content = _read_skill("verifying-specs")
        assert "archiving-specs" in content

    def test_archiving_specs_called_by_finishing(self):
        content = _read_skill("archiving-specs")
        assert "finishing" in content.lower()

    def test_archiving_specs_requires_verification(self):
        content = _read_skill("archiving-specs")
        assert "verifying-specs" in content or "verified" in content.lower()

    def test_finishing_runs_verify_then_archive(self):
        """Finishing must run verify-specs before archive-specs."""
        content = _read_skill("finishing-a-development-branch")
        verify_pos = content.find("verify-specs")
        archive_pos = content.find("archive-specs")
        assert verify_pos > 0, "verify-specs not found in finishing skill"
        assert archive_pos > 0, "archive-specs not found in finishing skill"
        assert verify_pos < archive_pos, (
            "verify-specs must appear before archive-specs in finishing skill"
        )


class TestWorkflowOptInBehavior:
    """The specs workflow is opt-in -- existing workflows must continue unchanged."""

    def test_brainstorming_makes_specs_optional(self):
        content = _read_skill("brainstorming")
        lower = content.lower()
        assert "would you like" in lower or "opt" in lower or "recommended" in lower, (
            "Brainstorming must present specs as optional, not mandatory"
        )

    def test_writing_plans_conditional_on_specs(self):
        """Plans should only include scenario tables when specs exist."""
        content = _read_skill("writing-plans")
        lower = content.lower()
        assert "when specs" in lower or "if specs" in lower or "specs-dir exists" in lower, (
            "Writing-plans must conditionally include scenarios based on specs existence"
        )

    def test_codex_conditional_on_specs(self):
        """Codex skill should only include spec contracts when specs exist."""
        content = _read_skill("codex-subagent-driven-development")
        lower = content.lower()
        assert "if specs" in lower or "if the plan references" in lower or "when specs" in lower, (
            "Codex skill must conditionally include spec contracts"
        )

    def test_finishing_skips_when_no_specs(self):
        content = _read_skill("finishing-a-development-branch")
        lower = content.lower()
        assert "skip" in lower or "no specs" in lower or "if no" in lower
