"""Test 7: Verify delta spec format parsing and validation."""

import pytest

from conftest import _parse_delta_spec, _read_skill


class TestDeltaSpecParsing:
    """Parser must correctly extract ADDED/MODIFIED/REMOVED sections."""

    VALID_DELTA = """# Greeter Delta Spec

## ADDED

### Personalized Greeting
GIVEN a user provides their name
WHEN the greeter is invoked
THEN a greeting containing their name is returned

### Default Greeting
GIVEN no name is provided
WHEN the greeter is invoked
THEN a default greeting is returned

## MODIFIED

### Greeting Format
**Was:** Plain text greeting
**Now:** Markdown-formatted greeting
**Reason:** Better readability in chat interfaces

GIVEN a name is provided
WHEN the greeter is invoked
THEN the greeting uses markdown bold for the name

## REMOVED

### Legacy Salutation
**Was:** Formal salutation with title
**Reason:** Simplified to first-name-only greeting
"""

    def test_parses_added_section(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        assert len(result["ADDED"]) == 2
        assert result["ADDED"][0]["name"] == "Personalized Greeting"
        assert result["ADDED"][1]["name"] == "Default Greeting"

    def test_parses_added_scenarios(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        scenario = result["ADDED"][0]["scenarios"][0]
        assert "GIVEN" in scenario["given"]
        assert "WHEN" in scenario["when"]
        assert "THEN" in scenario["then"]

    def test_parses_modified_section(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        assert len(result["MODIFIED"]) == 1
        assert result["MODIFIED"][0]["name"] == "Greeting Format"

    def test_parses_modified_metadata(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        meta = result["MODIFIED"][0]["meta"]
        assert "was" in meta
        assert "now" in meta
        assert "reason" in meta

    def test_parses_modified_scenarios(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        scenarios = result["MODIFIED"][0]["scenarios"]
        assert len(scenarios) == 1
        assert "GIVEN" in scenarios[0]["given"]

    def test_parses_removed_section(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        assert len(result["REMOVED"]) == 1
        assert result["REMOVED"][0]["name"] == "Legacy Salutation"

    def test_removed_has_was_and_reason(self):
        result = _parse_delta_spec(self.VALID_DELTA)
        meta = result["REMOVED"][0]["meta"]
        assert "was" in meta
        assert "reason" in meta


class TestDeltaSpecValidation:
    """Validate constraints on delta spec content."""

    def test_empty_content_returns_empty_sections(self):
        result = _parse_delta_spec("")
        assert result["ADDED"] == []
        assert result["MODIFIED"] == []
        assert result["REMOVED"] == []

    def test_scenario_requires_all_three_parts(self):
        """A complete scenario needs GIVEN, WHEN, and THEN."""
        incomplete = """# Test Delta

## ADDED

### Incomplete Behavior
GIVEN some precondition
WHEN some action
"""
        result = _parse_delta_spec(incomplete)
        scenario = result["ADDED"][0]["scenarios"][0]
        assert "given" in scenario
        assert "when" in scenario
        assert "then" not in scenario  # Missing THEN

    def test_multiple_scenarios_per_behavior(self):
        multi = """# Test Delta

## ADDED

### Multi Behavior
GIVEN condition A
WHEN action A
THEN result A

GIVEN condition B
WHEN action B
THEN result B
"""
        result = _parse_delta_spec(multi)
        assert len(result["ADDED"][0]["scenarios"]) == 2

    def test_only_added_section(self):
        """Delta with only ADDED (no MODIFIED/REMOVED) is valid for new features."""
        added_only = """# New Feature Delta

## ADDED

### New Behavior
GIVEN precondition
WHEN action
THEN result
"""
        result = _parse_delta_spec(added_only)
        assert len(result["ADDED"]) == 1
        assert result["MODIFIED"] == []
        assert result["REMOVED"] == []


class TestDeltaSpecFileConvention:
    """Delta spec files must follow naming conventions."""

    def test_writing_specs_documents_naming(self):
        """SKILL.md should document the <component>-delta.md naming convention."""
        content = _read_skill("writing-specs")
        assert "-delta.md" in content, (
            "Writing-specs doesn't document the -delta.md naming convention"
        )

    def test_writing_specs_documents_one_component_per_file(self):
        content = _read_skill("writing-specs")
        assert "one component per" in content.lower() or "One component per" in content, (
            "Writing-specs doesn't enforce one component per delta file"
        )
