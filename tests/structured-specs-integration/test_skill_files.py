"""Test 1: Verify new skill files exist with correct structure and frontmatter."""

import os

import pytest

from conftest import SKILLS_DIR, _extract_frontmatter, _read_skill


NEW_SKILLS = ["writing-specs", "verifying-specs", "archiving-specs"]


class TestSkillFileExistence:
    """All three new skills must exist as SKILL.md files."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_directory_exists(self, skill_name):
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        assert os.path.isdir(skill_dir), f"Skill directory missing: {skill_dir}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_md_exists(self, skill_name):
        skill_file = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        assert os.path.isfile(skill_file), f"SKILL.md missing: {skill_file}"


class TestSkillFrontmatter:
    """Frontmatter must have name and description fields per CLAUDE.md spec."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_name_field(self, skill_name):
        content = _read_skill(skill_name)
        fm = _extract_frontmatter(content)
        assert fm.get("name"), f"{skill_name} missing 'name' in frontmatter"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_name_matches_directory(self, skill_name):
        content = _read_skill(skill_name)
        fm = _extract_frontmatter(content)
        assert fm["name"] == skill_name, (
            f"Frontmatter name '{fm['name']}' does not match directory '{skill_name}'"
        )

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_description_field(self, skill_name):
        content = _read_skill(skill_name)
        fm = _extract_frontmatter(content)
        assert fm.get("description"), f"{skill_name} missing 'description' in frontmatter"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_description_starts_with_use_when(self, skill_name):
        content = _read_skill(skill_name)
        fm = _extract_frontmatter(content)
        assert fm["description"].startswith("Use when"), (
            f"{skill_name} description must start with 'Use when', got: '{fm['description'][:40]}...'"
        )

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_under_1024_chars(self, skill_name):
        content = _read_skill(skill_name)
        fm = _extract_frontmatter(content)
        total = len(fm.get("name", "")) + len(fm.get("description", ""))
        assert total <= 1024, (
            f"{skill_name} frontmatter total {total} chars exceeds 1024 limit"
        )


class TestSkillContent:
    """Skills must contain required sections per design plan."""

    def test_writing_specs_has_process_section(self):
        content = _read_skill("writing-specs")
        assert "## The Process" in content

    def test_writing_specs_has_delta_spec_format(self):
        content = _read_skill("writing-specs")
        assert "## ADDED" in content
        assert "## MODIFIED" in content
        assert "## REMOVED" in content

    def test_writing_specs_has_given_when_then(self):
        content = _read_skill("writing-specs")
        assert "GIVEN" in content
        assert "WHEN" in content
        assert "THEN" in content

    def test_writing_specs_has_proposal_template(self):
        content = _read_skill("writing-specs")
        assert "proposal.md" in content
        assert "## Intent" in content
        assert "## Scope" in content

    def test_writing_specs_has_living_specs_check(self):
        content = _read_skill("writing-specs")
        assert "_living" in content
        assert "Checking for Living Specs" in content

    def test_verifying_specs_has_three_checks(self):
        content = _read_skill("verifying-specs")
        assert "Completeness" in content
        assert "Correctness" in content
        assert "Coherence" in content

    def test_verifying_specs_has_completeness_report(self):
        content = _read_skill("verifying-specs")
        assert "## Completeness Report" in content
        assert "COVERED" in content
        assert "MISSING" in content

    def test_verifying_specs_has_correctness_report(self):
        content = _read_skill("verifying-specs")
        assert "## Correctness Report" in content
        assert "CORRECT" in content
        assert "INCORRECT" in content

    def test_verifying_specs_has_coherence_report(self):
        content = _read_skill("verifying-specs")
        assert "## Coherence Report" in content

    def test_verifying_specs_has_blocking_rules(self):
        content = _read_skill("verifying-specs")
        assert "## Blocking Rules" in content
        assert "FAIL" in content

    def test_verifying_specs_has_final_verdict(self):
        content = _read_skill("verifying-specs")
        assert "PASS" in content
        assert "Overall" in content

    def test_archiving_specs_has_process_section(self):
        content = _read_skill("archiving-specs")
        assert "## The Process" in content

    def test_archiving_specs_handles_added(self):
        content = _read_skill("archiving-specs")
        assert "ADDED" in content
        assert "append to living spec" in content

    def test_archiving_specs_handles_modified(self):
        content = _read_skill("archiving-specs")
        assert "MODIFIED" in content
        assert "replace" in content.lower()

    def test_archiving_specs_handles_removed(self):
        content = _read_skill("archiving-specs")
        assert "REMOVED" in content
        assert "Change History" in content

    def test_archiving_specs_has_archive_step(self):
        content = _read_skill("archiving-specs")
        assert "_archive" in content

    def test_archiving_specs_requires_verification(self):
        content = _read_skill("archiving-specs")
        assert "verify" in content.lower()
        assert "Prerequisites" in content

    def test_archiving_specs_is_idempotent(self):
        content = _read_skill("archiving-specs")
        assert "idempotent" in content.lower() or "no-op" in content.lower()


class TestSkillAnnouncement:
    """Each skill must announce itself at start per convention."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_announce_instruction(self, skill_name):
        content = _read_skill(skill_name)
        assert "Announce at start" in content, (
            f"{skill_name} missing 'Announce at start' instruction"
        )


class TestSkillIntegration:
    """Each skill must document what it integrates with."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_integration_section(self, skill_name):
        content = _read_skill(skill_name)
        assert "## Integration" in content, (
            f"{skill_name} missing '## Integration' section"
        )
