"""Lifecycle skill support for LIGHT mini-spec feature directories."""

import re

from conftest import _read_skill


class TestSpecDrivenTddMiniSpecFingerprint:
    def test_step1_reads_mini_or_delta_specs_by_mode(self):
        content = _read_skill("spec-driven-tdd")
        step1 = re.search(r"### Step 1.*?(?=### Step 2|$)", content, re.DOTALL)
        assert step1, "Step 1 section not found"
        text = step1.group(0)
        assert "mini.md" in text
        assert "specs/*-delta.md" in text
        assert "GIVEN/WHEN/THEN" in text

    def test_fingerprint_for_light_covers_mini_md_alone(self):
        content = _read_skill("spec-driven-tdd")
        step2 = re.search(r"### Step 2.*?(?=### Step 3|$)", content, re.DOTALL)
        assert step2, "Step 2 section not found"
        text = step2.group(0)
        assert "mini.md alone" in text or "sha256sum mini.md" in text
        assert "proposal.md design.md specs/*-delta.md" in text

    def test_reentry_recomputes_mode_appropriate_fingerprint(self):
        content = _read_skill("spec-driven-tdd")
        step4 = re.search(r"### Step 4.*?(?=## Why|$)", content, re.DOTALL)
        assert step4, "Step 4 section not found"
        text = step4.group(0)
        assert "mini.md" in text
        assert "mode" in text.lower()
        assert "reopen" in text.lower() or "flip it back to `[ ]`" in text

    def test_mini_spec_scenarios_are_contractual(self):
        content = _read_skill("spec-driven-tdd")
        assert "mini.md scenario" in content or "mini-spec scenario" in content
        assert "no scenario is treated as optional" in content


class TestVerifyingSpecsMiniSpecLifecycle:
    def test_locate_specs_reads_mini_md_when_present(self):
        content = _read_skill("verifying-specs")
        step1 = re.search(r"### Step 1.*?(?=### Step 2|$)", content, re.DOTALL)
        assert step1, "Step 1 section not found"
        text = step1.group(0)
        assert "mini.md" in text
        assert "GIVEN/WHEN/THEN" in text
        assert "specs/*-delta.md" in text or "*-delta.md" in text

    def test_completeness_report_can_source_mini_md(self):
        content = _read_skill("verifying-specs")
        assert "mini.md" in content
        assert "scenario→test coverage" in content or "scenario-to-test coverage" in content
        assert "COVERED" in content
        assert "MISSING" in content

    def test_coherence_check_includes_mini_specs_against_living(self):
        content = _read_skill("verifying-specs")
        step4 = re.search(r"### Step 4: Coherence Check.*?(?=### Step 4a|$)", content, re.DOTALL)
        assert step4, "Step 4 coherence section not found"
        text = step4.group(0)
        assert "mini.md" in text
        assert "_living" in text
        assert "contradict" in text.lower()


class TestArchivingSpecsMiniSpecLifecycle:
    def test_locate_specs_allows_mini_md(self):
        content = _read_skill("archiving-specs")
        step1 = re.search(r"### Step 1.*?(?=### Step 2|$)", content, re.DOTALL)
        assert step1, "Step 1 section not found"
        text = step1.group(0)
        assert "mini.md" in text
        assert "*-delta.md" in text

    def test_archive_merges_mini_scenarios_with_attribution(self):
        content = _read_skill("archiving-specs")
        assert "mini.md scenarios" in content or "mini-spec scenarios" in content
        assert "docs/specs/_living/<component>.md" in content
        assert "Added: YYYY-MM-DD via <feature>" in content

    def test_pre_archive_completeness_allows_light_missing_proposal_design(self):
        content = _read_skill("archiving-specs")
        step26 = re.search(r"### Step 2.6.*?(?=### Step 3|$)", content, re.DOTALL)
        assert step26, "Step 2.6 section not found"
        text = step26.group(0)
        assert "mini.md" in text
        assert "proposal.md / design.md" in text or "proposal.md" in text
        assert "LIGHT" in text
