"""Test 6: Verify finishing-a-development-branch gates on spec verification."""

from conftest import _read_skill


class TestFinishingSpecVerification:
    """Finishing skill must run spec verification before merge and archive after."""

    def test_has_step_1b_verify_specs(self):
        content = _read_skill("finishing-a-development-branch")
        assert "Step 1b" in content or "Verify Specs" in content, (
            "Finishing skill missing Step 1b for spec verification"
        )

    def test_checks_for_specs_directory(self):
        content = _read_skill("finishing-a-development-branch")
        assert "docs/specs/" in content or "specs" in content.lower(), (
            "Finishing skill doesn't check for specs directory"
        )

    def test_runs_verify_specs_skill(self):
        content = _read_skill("finishing-a-development-branch")
        assert "verify-specs" in content, (
            "Finishing skill doesn't invoke verify-specs"
        )

    def test_blocks_merge_on_failure(self):
        content = _read_skill("finishing-a-development-branch")
        lower = content.lower()
        assert "stop" in lower or "block" in lower or "fail" in lower, (
            "Finishing skill doesn't block merge when spec verification fails"
        )

    def test_runs_archive_after_merge(self):
        content = _read_skill("finishing-a-development-branch")
        assert "archive-specs" in content, (
            "Finishing skill doesn't invoke archive-specs after merge"
        )

    def test_skips_when_no_specs(self):
        """Should skip spec verification if no specs directory exists."""
        content = _read_skill("finishing-a-development-branch")
        lower = content.lower()
        assert "skip" in lower or "no specs" in lower or "if no" in lower, (
            "Finishing skill doesn't handle absence of specs directory"
        )
