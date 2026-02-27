"""Test 4: Verify writing-plans skill incorporates scenario tables when specs exist."""

from conftest import _read_skill


class TestWritingPlansSpecsIntegration:
    """Writing-plans must include scenarios from delta specs in plan tasks."""

    def test_has_specs_dir_in_metadata(self):
        content = _read_skill("writing-plans")
        assert "specs-dir" in content, (
            "Writing-plans skill missing 'specs-dir' in plan metadata"
        )

    def test_has_scenarios_table_template(self):
        content = _read_skill("writing-plans")
        assert "Scenarios" in content, (
            "Writing-plans skill missing 'Scenarios' table in task template"
        )

    def test_scenarios_reference_delta_spec(self):
        content = _read_skill("writing-plans")
        assert "delta" in content.lower(), (
            "Writing-plans skill doesn't reference delta specs as scenario source"
        )

    def test_scenarios_table_has_columns(self):
        """Scenarios table should have ID, Scenario, and Source columns."""
        content = _read_skill("writing-plans")
        assert "ID" in content
        assert "Scenario" in content
        assert "Source" in content

    def test_given_when_then_mapping_to_tests(self):
        """Step 1 should map GIVEN->setup, WHEN->action, THEN->assertion."""
        content = _read_skill("writing-plans")
        lower = content.lower()
        has_mapping = (
            ("given" in lower and "setup" in lower)
            or ("when" in lower and "action" in lower)
            or ("then" in lower and "assertion" in lower)
        )
        assert has_mapping, (
            "Writing-plans doesn't map GIVEN/WHEN/THEN to test structure"
        )

    def test_specs_dir_is_optional(self):
        """specs-dir should be marked as optional metadata."""
        content = _read_skill("writing-plans")
        lower = content.lower()
        assert "optional" in lower or "when specs" in lower, (
            "Writing-plans doesn't indicate specs-dir is optional"
        )
