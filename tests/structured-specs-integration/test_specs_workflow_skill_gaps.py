"""Tests for specs-workflow-skill-gaps delta specs.

Covers:
- spec-driven-tdd: DEBT annotation step in TDD loop, unannotated compromise red flag
- verifying-specs: multi-language DEBT scan, progress.md Issues debt, Step 4e, namespace
- archiving-specs: pre-archive checks, system index update, six-step overview, namespace
"""

import re
import pytest
from conftest import _read_skill


# ---------------------------------------------------------------------------
# spec-driven-tdd skill
# ---------------------------------------------------------------------------

class TestSpecDrivenTddDebtAnnotation:
    """TDD Loop Includes Debt Annotation Step + Unannotated Compromise Is A Red Flag."""

    def _skill(self):
        return _read_skill("spec-driven-tdd")

    def test_step3_contains_debt_annotation_step(self):
        """Step 3 TDD loop must include a DEBT: annotation plus Issues entry step."""
        content = self._skill()
        # Find the Step 3 section
        step3_match = re.search(r"### Step 3.*?(?=### Step 4|## Why|## Common|## Red Flags|$)", content, re.DOTALL)
        assert step3_match, "Step 3 section not found in spec-driven-tdd SKILL.md"
        step3 = step3_match.group(0)
        assert "DEBT:" in step3, (
            "Step 3 must contain a 'DEBT:' annotation step for compromises"
        )
        assert "Issues" in step3, (
            "Step 3 must mention adding compromise to '## Issues' in progress.md"
        )

    def test_red_flags_includes_unannotated_compromise(self):
        """Red Flags section must list making a compromise without DEBT: annotation."""
        content = self._skill()
        red_flags_match = re.search(r"## Red Flags.*?(?=##|$)", content, re.DOTALL)
        assert red_flags_match, "Red Flags section not found in spec-driven-tdd SKILL.md"
        red_flags = red_flags_match.group(0)
        assert "DEBT:" in red_flags, (
            "Red Flags must include making a compromise without a DEBT: annotation"
        )


# ---------------------------------------------------------------------------
# verifying-specs skill
# ---------------------------------------------------------------------------

class TestVerifyingSpecsDebtScanMultiLanguage:
    """Collect Manual Debt Annotations — Step 4a must scan all comment syntaxes."""

    def _skill(self):
        return _read_skill("verifying-specs")

    def test_step4a_scans_hash_comments(self):
        """Step 4a must scan # DEBT: (Python) annotations."""
        content = self._skill()
        step4a_match = re.search(r"### Step 4a.*?(?=### Step 4b|## Step|### Step 5|## Blocking|$)", content, re.DOTALL)
        assert step4a_match, "Step 4a section not found in verifying-specs SKILL.md"
        step4a = step4a_match.group(0)
        assert "# DEBT:" in step4a or "`#`" in step4a or "'#'" in step4a or '"#"' in step4a or re.search(r'\bPython\b', step4a), (
            "Step 4a must mention # DEBT: (Python) comment syntax"
        )

    def test_step4a_scans_double_dash_comments(self):
        """Step 4a must scan -- DEBT: (SQL) annotations."""
        content = self._skill()
        step4a_match = re.search(r"### Step 4a.*?(?=### Step 4b|## Step|### Step 5|## Blocking|$)", content, re.DOTALL)
        assert step4a_match, "Step 4a section not found in verifying-specs SKILL.md"
        step4a = step4a_match.group(0)
        assert "-- DEBT:" in step4a or "`--`" in step4a or re.search(r'\bSQL\b', step4a), (
            "Step 4a must mention -- DEBT: (SQL) comment syntax"
        )

    def test_step4a_rg_command_uses_generic_pattern(self):
        """Step 4a rg command must match DEBT: in any comment syntax, not just //."""
        content = self._skill()
        step4a_match = re.search(r"### Step 4a.*?(?=### Step 4b|## Step|### Step 5|## Blocking|$)", content, re.DOTALL)
        assert step4a_match, "Step 4a section not found"
        step4a = step4a_match.group(0)
        # The rg pattern should search for "DEBT:" generically, not just "// DEBT:"
        rg_lines = [l for l in step4a.split("\n") if "rg" in l and "DEBT" in l]
        assert rg_lines, "Step 4a must contain an rg command scanning for DEBT:"
        rg_cmd = rg_lines[0]
        assert '"// DEBT:"' not in rg_cmd and "'// DEBT:'" not in rg_cmd, (
            "Step 4a rg command must not be limited to '// DEBT:' — must scan all comment syntaxes"
        )


class TestVerifyingSpecsProgressMdIssuesDebt:
    """Collect Debt From Progress.md Issues — Step 4b-2 pipeline."""

    def _skill(self):
        return _read_skill("verifying-specs")

    def test_step4b_or_section_references_progress_md_issues(self):
        """Step 4b or nearby section must reference progress.md Issues as a debt source."""
        content = self._skill()
        assert "progress.md" in content and "Issues" in content, (
            "verifying-specs SKILL.md must reference progress.md Issues as a debt source"
        )
        # Confirm they appear near each other (within 500 chars) in the debt pipeline section
        idx = content.find("4b")
        if idx == -1:
            idx = content.find("Step 4b")
        assert idx != -1, "Step 4b section not found in verifying-specs"
        surrounding = content[max(0, idx - 200):idx + 800]
        assert "progress.md" in surrounding, (
            "Step 4b must be near a reference to progress.md Issues debt"
        )

    def test_debt_summary_includes_progress_md_issues_count(self):
        """Technical Debt Summary must include a count of progress.md-Issues debt items."""
        content = self._skill()
        summary_match = re.search(r"## Technical Debt Summary.*?(?=##|$)", content, re.DOTALL)
        assert summary_match, "Technical Debt Summary section not found"
        summary = summary_match.group(0)
        assert "progress.md" in summary or "Issues" in summary, (
            "Technical Debt Summary must include count of progress.md-Issues debt items"
        )

    def test_missing_progress_md_does_not_fail_verification(self):
        """Verification must continue gracefully when progress.md is missing."""
        content = self._skill()
        # Somewhere in step 4b-ish area the skill must say missing progress.md is tolerated
        assert re.search(r"progress\.md.*?(missing|absent|tolerat|not exist|continue)", content, re.IGNORECASE) or \
               re.search(r"(missing|absent|tolerat|not exist|continue).*?progress\.md", content, re.IGNORECASE), (
            "verifying-specs must state that missing progress.md is tolerated (verification continues)"
        )


class TestVerifyingSpecsSkipStep4ThreeSources:
    """Skip Debt Identification When No Debt Found — must check all 3 sources."""

    def _skill(self):
        return _read_skill("verifying-specs")

    def test_skip_condition_mentions_progress_md_issues(self):
        """The 'skip Step 4' condition must include no debt-bearing progress.md Issues."""
        content = self._skill()
        # Find the skip condition text
        skip_match = re.search(
            r"(no.*REMOVED.*no.*DEBT|no.*DEBT.*no.*REMOVED|skip.*Step 4|Step 4.*skipp).*",
            content, re.IGNORECASE | re.DOTALL
        )
        assert skip_match, "Skip Step 4 condition not found in verifying-specs"
        # The skip condition must now reference progress.md
        skip_area = content[max(0, skip_match.start() - 100):skip_match.end() + 500]
        assert "progress.md" in skip_area, (
            "Skip Step 4 condition must also check for no debt-bearing progress.md Issues entries"
        )


class TestVerifyingSpecsStep4eSingleIfNo:
    """Prompt User For Cleanup — Step 4e must have exactly one 'If no:' branch."""

    def _skill(self):
        return _read_skill("verifying-specs")

    def test_step4e_has_exactly_one_if_no_branch(self):
        """Step 4e must contain exactly one 'If no:' branch."""
        content = self._skill()
        step4e_match = re.search(r"### Step 4e.*?(?=### Step 5|## Step 5|## Blocking|$)", content, re.DOTALL)
        assert step4e_match, "Step 4e section not found in verifying-specs SKILL.md"
        step4e = step4e_match.group(0)
        if_no_count = len(re.findall(r"If no:", step4e, re.IGNORECASE))
        assert if_no_count == 1, (
            f"Step 4e must have exactly one 'If no:' branch, found {if_no_count}"
        )

    def test_step4e_if_no_routes_to_archiving(self):
        """The single 'If no:' branch in Step 4e must route to archiving-specs."""
        content = self._skill()
        step4e_match = re.search(r"### Step 4e.*?(?=### Step 5|## Step 5|## Blocking|$)", content, re.DOTALL)
        assert step4e_match, "Step 4e section not found"
        step4e = step4e_match.group(0)
        if_no_idx = step4e.lower().find("if no:")
        assert if_no_idx != -1, "No 'If no:' branch found in Step 4e"
        after_if_no = step4e[if_no_idx:if_no_idx + 200]
        assert "archiving" in after_if_no.lower(), (
            "The 'If no:' branch in Step 4e must route to archiving-specs"
        )


class TestVerifyingSpecsNamespaceConsistency:
    """Cross-References Use A Consistent Resolvable Namespace."""

    def _skill(self):
        return _read_skill("verifying-specs")

    def test_no_bare_superpowers_references(self):
        """verifying-specs must not use the bare 'superpowers:' namespace for skill references."""
        content = self._skill()
        # Look for bare superpowers: skill references (not superpowerwithcodex:)
        bare_refs = re.findall(r"(?<!\w)`superpowers:[a-z-]+`|`superpowers:[a-z-]+`", content)
        assert not bare_refs, (
            f"verifying-specs uses bare 'superpowers:' namespace — should use 'superpowerwithcodex:': {bare_refs}"
        )


# ---------------------------------------------------------------------------
# archiving-specs skill
# ---------------------------------------------------------------------------

class TestArchivingSpecsPreArchiveChecks:
    """Pre-archive completeness checks (Step 2.6)."""

    def _skill(self):
        return _read_skill("archiving-specs")

    def test_missing_progress_md_blocks_archive(self):
        """Skill must state that missing progress.md blocks archiving with stop/ask behavior."""
        content = self._skill()
        assert re.search(r"progress\.md", content), "archiving-specs must reference progress.md"
        assert re.search(
            r"(progress\.md.*?(block|stop|STOP|prevents|require)|"
            r"(block|stop|STOP|prevents|require).*?progress\.md)",
            content, re.IGNORECASE
        ), "archiving-specs must state that missing progress.md blocks archive"

    def test_missing_proposal_or_design_warns_without_blocking(self):
        """Skill must warn about missing proposal.md/design.md but continue."""
        content = self._skill()
        assert re.search(r"(proposal\.md|design\.md)", content), (
            "archiving-specs must reference proposal.md or design.md"
        )
        assert re.search(
            r"(warn|warning|continue|without blocking)",
            content, re.IGNORECASE
        ), "archiving-specs must issue a warning (not block) for missing proposal/design"

    def test_stray_spec_files_relocated_before_archive(self):
        """Skill must describe moving stray *.md files from feature root to specs/."""
        content = self._skill()
        assert re.search(
            r"(stray|root.*spec|spec.*root|moved.*specs/|specs/.*moved)",
            content, re.IGNORECASE
        ), "archiving-specs must describe relocating stray spec files from feature root to specs/"

    def test_junk_files_removed_before_archive(self):
        """Skill must describe removing junk files (copies, editor backups)."""
        content = self._skill()
        assert re.search(
            r"(junk|copy\.\*|editor backup|\* copy|\bbackup\b)",
            content, re.IGNORECASE
        ), "archiving-specs must describe removing junk files (copies, editor backups)"


class TestArchivingSpecsSystemIndexUpdate:
    """System Index Updated On Archive (Step 2.5) and related scenarios."""

    def _skill(self):
        return _read_skill("archiving-specs")

    def test_skill_has_index_update_step(self):
        """Skill must contain a step for updating docs/specs/_living/ARCHITECTURE.md."""
        content = self._skill()
        assert "ARCHITECTURE.md" in content, (
            "archiving-specs must reference docs/specs/_living/ARCHITECTURE.md index"
        )
        assert re.search(r"(index|Index)", content), (
            "archiving-specs must describe an index update step"
        )

    def test_unindexed_living_spec_detection(self):
        """Skill must describe detecting living spec files not in ARCHITECTURE.md."""
        content = self._skill()
        assert re.search(
            r"(unindexed|not indexed|not reference|missing.*index|index.*missing)",
            content, re.IGNORECASE
        ), "archiving-specs must describe detecting living specs not present in ARCHITECTURE.md"

    def test_missing_architecture_md_is_tolerated(self):
        """Skill must state that missing ARCHITECTURE.md is tolerated (skip, not fail)."""
        content = self._skill()
        assert re.search(
            r"ARCHITECTURE\.md.*?(skip|tolerat|does not exist|not exist|absent|optional)",
            content, re.IGNORECASE
        ) or re.search(
            r"(skip|tolerat|does not exist|not exist|absent|optional).*?ARCHITECTURE\.md",
            content, re.IGNORECASE
        ), "archiving-specs must tolerate missing ARCHITECTURE.md (skip without failure)"

    def test_offer_to_create_index_at_three_or_more_living_specs(self):
        """Skill must mention offering to create ARCHITECTURE.md when 3+ living specs exist."""
        content = self._skill()
        assert re.search(r"(three|3).*?(living spec|ARCHITECTURE|index)", content, re.IGNORECASE) or \
               re.search(r"(living spec|ARCHITECTURE|index).*?(three|3)", content, re.IGNORECASE), (
            "archiving-specs must offer to create index when three or more living specs exist"
        )


class TestArchivingSpecsOverviewSixSteps:
    """Overview Lists Six Steps Including Index Update."""

    def _skill(self):
        return _read_skill("archiving-specs")

    def test_overview_has_six_numbered_steps(self):
        """Overview section must list exactly six numbered steps."""
        content = self._skill()
        overview_match = re.search(r"## Overview.*?(?=##)", content, re.DOTALL)
        assert overview_match, "Overview section not found in archiving-specs SKILL.md"
        overview = overview_match.group(0)
        numbered_steps = re.findall(r"^\d+\.", overview, re.MULTILINE)
        assert len(numbered_steps) == 6, (
            f"Overview must list 6 numbered steps, found {len(numbered_steps)}: {numbered_steps}"
        )

    def test_overview_includes_index_update_step(self):
        """Overview numbered list must include index update step."""
        content = self._skill()
        overview_match = re.search(r"## Overview.*?(?=##)", content, re.DOTALL)
        assert overview_match, "Overview section not found"
        overview = overview_match.group(0)
        assert re.search(r"(index|ARCHITECTURE)", overview, re.IGNORECASE), (
            "Overview must include a step for updating the system index (ARCHITECTURE.md)"
        )


class TestArchivingSpecsNamespaceConsistency:
    """Cross-References Use A Consistent Resolvable Namespace."""

    def _skill(self):
        return _read_skill("archiving-specs")

    def test_no_bare_superpowers_references(self):
        """archiving-specs must not use the bare 'superpowers:' namespace for skill references."""
        content = self._skill()
        bare_refs = re.findall(r"`superpowers:[a-z-]+`", content)
        assert not bare_refs, (
            f"archiving-specs uses bare 'superpowers:' namespace — should use 'superpowerwithcodex:': {bare_refs}"
        )
