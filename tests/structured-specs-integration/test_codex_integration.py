"""Test 5: Verify codex-subagent-driven-development skill enforces spec contracts."""

from conftest import _read_skill


class TestCodexSpecContracts:
    """Codex subagent skill must include spec contracts in dispatch prompts."""

    def test_step_3a_reads_delta_specs(self):
        """Step 3a (RED) should read delta specs and derive tests from scenarios."""
        content = _read_skill("codex-subagent-driven-development")
        assert "delta spec" in content.lower() or "specs-dir" in content.lower(), (
            "Codex skill Step 3a doesn't reference delta specs"
        )

    def test_step_3a_derives_tests_from_scenarios(self):
        content = _read_skill("codex-subagent-driven-development")
        lower = content.lower()
        assert "given" in lower and "when" in lower and "then" in lower, (
            "Codex skill doesn't mention deriving tests from GIVEN/WHEN/THEN"
        )

    def test_step_3b_has_specification_contract(self):
        """Step 3b (GREEN) Codex prompt must include Specification Contract section."""
        content = _read_skill("codex-subagent-driven-development")
        assert "Specification Contract" in content, (
            "Codex skill missing 'Specification Contract' in dispatch prompt"
        )

    def test_step_3b_scenarios_are_inviolable(self):
        content = _read_skill("codex-subagent-driven-development")
        assert "inviolable" in content.lower(), (
            "Codex skill doesn't mark scenarios as inviolable requirements"
        )

    def test_specs_dir_in_read_only_boundary(self):
        """docs/specs/ must be in the read-only boundary list for Codex."""
        content = _read_skill("codex-subagent-driven-development")
        assert "docs/specs/" in content, (
            "Codex skill doesn't include docs/specs/ in read-only boundaries"
        )

    def test_step_3d_verifies_scenario_coverage(self):
        """Step 3d (Review) should flag uncovered scenarios as Critical."""
        content = _read_skill("codex-subagent-driven-development")
        lower = content.lower()
        has_review_check = (
            "uncovered scenario" in lower
            or ("scenario" in lower and "critical" in lower)
        )
        assert has_review_check, (
            "Codex skill Step 3d doesn't verify scenario coverage in review"
        )
