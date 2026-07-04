"""Learn skill and handover wrap-up integration conventions."""

import os

from conftest import SKILLS_DIR, _extract_frontmatter, _read_skill


LEARN_SKILL = "learn"


class TestLearnSkillFile:
    def test_skill_file_exists(self):
        path = os.path.join(SKILLS_DIR, LEARN_SKILL, "SKILL.md")
        assert os.path.isfile(path)

    def test_frontmatter_shape(self):
        content = _read_skill(LEARN_SKILL)
        frontmatter = _extract_frontmatter(content)

        assert frontmatter == {
            "name": LEARN_SKILL,
            "description": frontmatter.get("description"),
        }
        assert frontmatter["description"].startswith("Use when")
        assert "lesson" in frontmatter["description"]
        assert "pattern" in frontmatter["description"]
        assert "proposal" in frontmatter["description"]
        assert len(frontmatter["name"]) + len(frontmatter["description"]) <= 1024

    def test_documents_lesson_entry_shape(self):
        content = _read_skill(LEARN_SKILL)

        assert "docs/lessons.md" in content
        assert "~/.claude/lessons-common.md" in content
        assert "## [tag: <kebab-case-tag>] <Title>" in content
        for field in (
            "- Symptom:",
            "- Root cause:",
            "- Correct approach:",
            "- Occurrences:",
            "- Level:",
        ):
            assert field in content


class TestLearnBehaviorText:
    def test_requires_confirmation_for_active_capture_and_confidence(self):
        content = _read_skill(LEARN_SKILL).lower()

        assert "shows the complete entry" in content
        assert "explicit user confirmation" in content
        assert "certainty never bypasses" in content
        assert "writes nothing" in content

    def test_passive_scan_presents_candidates_and_empty_result(self):
        content = _read_skill(LEARN_SKILL).lower()

        for signal in (
            "user corrected the approach",
            "debug loop exceeded 2 rounds",
            "technical decision",
            "same problem class recurred",
        ):
            assert signal in content
        assert "candidate list" in content
        assert "no lesson candidates were found" in content
        assert "does not invent entries" in content

    def test_dedup_and_root_cause_rules_are_tag_based(self):
        content = _read_skill(LEARN_SKILL).lower()

        assert "dedup by tag" in content
        assert "not title" in content
        assert "existing entry gains an occurrence" in content
        assert "different root cause" in content
        assert "distinct tag" in content

    def test_promotion_and_proposal_rules_are_confirmation_gated(self):
        content = _read_skill(LEARN_SKILL)
        lower = content.lower()

        assert "2 occurrences" in lower
        assert "level: pattern" in lower
        assert "sync only after" in lower
        assert "3 occurrences" in lower
        assert "upgrade proposal" in lower
        assert "target skill" in lower
        assert "suggested constraint" in lower
        assert "supporting occurrence records" in lower
        assert "never edits the target skill" in lower
        assert "writing-skills" in content

    def test_declines_missing_file_and_unwritable_shared_file(self):
        content = _read_skill(LEARN_SKILL).lower()

        assert "declined item is discarded" in content
        assert "without being written" in content
        assert "creates the file with a header" in content
        assert "unwritable" in content
        assert "keeps the project-level entry intact" in content
        assert "does not retry silently" in content


class TestHandoverManagerLearnIntegration:
    def test_wrap_up_invokes_learn_after_latest_is_updated(self):
        content = _read_skill("handover-manager")
        lower = content.lower()

        latest_index = content.index("docs/handovers/LATEST.md")
        learn_index = lower.index("learn")

        assert "passive scan" in lower
        assert learn_index > latest_index
        assert "candidate list" in lower
        assert "no candidates" in lower
        assert "before the session is considered wrapped up" in lower

    def test_learn_scan_does_not_modify_handover_output(self):
        content = _read_skill("handover-manager").lower()

        assert "learn scan runs after the handover is written" in content
        assert "never modifies" in content
        assert "latest.md remain exactly as generated" in content
