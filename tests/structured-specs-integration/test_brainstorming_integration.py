"""Test 3: Verify brainstorming skill offers structured specs opt-in."""

from conftest import _read_skill


class TestBrainstormingSpecsOptIn:
    """Brainstorming must offer structured specs after design completion."""

    def test_has_structured_specifications_section(self):
        content = _read_skill("brainstorming")
        assert "Structured Specifications" in content, (
            "Brainstorming skill missing 'Structured Specifications' section"
        )

    def test_offers_opt_in_question(self):
        content = _read_skill("brainstorming")
        assert "structured specs" in content.lower() or "testable scenarios" in content.lower(), (
            "Brainstorming skill doesn't ask about structured specs"
        )

    def test_references_write_specs_skill(self):
        content = _read_skill("brainstorming")
        assert "write-specs" in content, (
            "Brainstorming skill doesn't reference write-specs"
        )

    def test_supports_opt_out(self):
        """User should be able to decline specs and keep legacy format."""
        content = _read_skill("brainstorming")
        lower = content.lower()
        assert "no" in lower or "decline" in lower or "legacy" in lower, (
            "Brainstorming skill doesn't support declining structured specs"
        )

    def test_specs_section_between_docs_and_implementation(self):
        """Structured specs section should appear after documentation."""
        content = _read_skill("brainstorming")
        specs_pos = content.find("Structured Specifications")
        assert specs_pos > 0, "Structured Specifications section not found"
