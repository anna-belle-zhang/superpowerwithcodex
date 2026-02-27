"""Test 8: Verify directory convention is documented and consistent across skills."""

import os

from conftest import _read_skill, REPO_ROOT


class TestDirectoryConventionDocumented:
    """All skills must reference the correct directory structure."""

    def test_writing_specs_references_feature_dir(self):
        content = _read_skill("writing-specs")
        assert "docs/specs/<feature>/" in content or "docs/specs/" in content

    def test_writing_specs_references_proposal(self):
        content = _read_skill("writing-specs")
        assert "proposal.md" in content

    def test_writing_specs_references_design(self):
        content = _read_skill("writing-specs")
        assert "design.md" in content

    def test_writing_specs_references_specs_subdir(self):
        content = _read_skill("writing-specs")
        assert "specs/" in content

    def test_verifying_specs_references_delta_files(self):
        content = _read_skill("verifying-specs")
        assert "-delta.md" in content or "delta" in content.lower()

    def test_archiving_specs_references_living_dir(self):
        content = _read_skill("archiving-specs")
        assert "_living" in content

    def test_archiving_specs_references_archive_dir(self):
        content = _read_skill("archiving-specs")
        assert "_archive" in content

    def test_archiving_specs_uses_date_prefix(self):
        """Archive directory should use YYYY-MM-DD-<feature> naming."""
        content = _read_skill("archiving-specs")
        assert "YYYY-MM-DD" in content


class TestDirectoryConventionInClaudeMd:
    """CLAUDE.md must document the full directory convention."""

    def test_claude_md_has_specs_directory_section(self):
        claude_md = os.path.join(REPO_ROOT, "CLAUDE.md")
        with open(claude_md, "r", encoding="utf-8") as f:
            content = f.read()
        assert "docs/specs/" in content
        assert "_living" in content
        assert "_archive" in content

    def test_claude_md_has_delta_format(self):
        claude_md = os.path.join(REPO_ROOT, "CLAUDE.md")
        with open(claude_md, "r", encoding="utf-8") as f:
            content = f.read()
        assert "## ADDED" in content
        assert "GIVEN" in content
        assert "WHEN" in content
        assert "THEN" in content


class TestDirectoryStructureSetup:
    """Verify directory creation works correctly in temporary environment."""

    def test_tmp_specs_dir_structure(self, tmp_specs_dir):
        assert os.path.isdir(tmp_specs_dir["feature"])
        assert os.path.isdir(tmp_specs_dir["specs"])
        assert os.path.isdir(tmp_specs_dir["living"])
        assert os.path.isdir(tmp_specs_dir["archive"])

    def test_can_create_proposal(self, tmp_specs_dir):
        proposal_path = os.path.join(tmp_specs_dir["feature"], "proposal.md")
        with open(proposal_path, "w") as f:
            f.write("# Test Proposal\n\n## Intent\nTest intent\n")
        assert os.path.isfile(proposal_path)

    def test_can_create_design(self, tmp_specs_dir):
        design_path = os.path.join(tmp_specs_dir["feature"], "design.md")
        with open(design_path, "w") as f:
            f.write("# Test Design\n\n## Architecture\nTest arch\n")
        assert os.path.isfile(design_path)

    def test_can_create_delta_spec(self, tmp_specs_dir):
        delta_path = os.path.join(tmp_specs_dir["specs"], "greeter-delta.md")
        with open(delta_path, "w") as f:
            f.write("# Greeter Delta Spec\n\n## ADDED\n\n### Hello\nGIVEN name\nWHEN greet\nTHEN hello\n")
        assert os.path.isfile(delta_path)

    def test_can_create_living_spec(self, tmp_specs_dir):
        living_path = os.path.join(tmp_specs_dir["living"], "greeter.md")
        with open(living_path, "w") as f:
            f.write("# Greeter - Living Spec\n\n## Behaviors\n\n### Hello\n")
        assert os.path.isfile(living_path)
