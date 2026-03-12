"""Integration tests for the technical debt cleanup workflow."""

import os

from conftest import COMMANDS_DIR, SKILLS_DIR, _extract_frontmatter, _read_command, _read_skill


NEW_SKILLS = ["cleanup-and-refactor", "code-simplification"]


class TestTechnicalDebtSkillFiles:
    """New technical debt skills must follow the repo's markdown skill conventions."""

    def test_cleanup_and_refactor_skill_exists(self):
        skill_file = os.path.join(SKILLS_DIR, "cleanup-and-refactor", "SKILL.md")
        assert os.path.isfile(skill_file), f"SKILL.md missing: {skill_file}"

    def test_code_simplification_skill_exists(self):
        skill_file = os.path.join(SKILLS_DIR, "code-simplification", "SKILL.md")
        assert os.path.isfile(skill_file), f"SKILL.md missing: {skill_file}"

    def test_new_skill_frontmatter(self):
        for skill_name in NEW_SKILLS:
            content = _read_skill(skill_name)
            fm = _extract_frontmatter(content)
            assert fm.get("name") == skill_name
            assert fm.get("description"), f"{skill_name} missing description"
            assert fm["description"].startswith("Use when"), (
                f"{skill_name} description must start with 'Use when'"
            )


class TestTechnicalDebtCommandRouting:
    """The user-facing cleanup command must route to the new skill."""

    def test_cleanup_and_refactor_command_exists(self):
        cmd_file = os.path.join(COMMANDS_DIR, "cleanup-and-refactor.md")
        assert os.path.isfile(cmd_file), f"Command file missing: {cmd_file}"

    def test_cleanup_and_refactor_command_frontmatter(self):
        content = _read_command("cleanup-and-refactor")
        fm = _extract_frontmatter(content)
        assert fm.get("description"), "cleanup-and-refactor command missing description"

    def test_cleanup_and_refactor_command_routes_to_skill(self):
        content = _read_command("cleanup-and-refactor")
        lower = content.lower()
        assert "cleanup-and-refactor" in content
        assert "follow" in lower or "use" in lower


class TestVerifyingSpecsDebtFlow:
    """verify-specs must advertise the new technical debt identification flow."""

    def test_verifying_specs_collects_manual_debt_annotations(self):
        content = _read_skill("verifying-specs")
        assert "// DEBT:" in content
        assert "file path" in content.lower()
        assert "line number" in content.lower()

    def test_verifying_specs_handles_removed_scenarios(self):
        content = _read_skill("verifying-specs")
        assert "REMOVED" in content
        assert "_living" in content
        assert "technical debt" in content.lower()

    def test_verifying_specs_writes_debt_files(self):
        content = _read_skill("verifying-specs")
        assert "technical-debt.md" in content
        assert "_technical-debt.md" in content
        assert "Build Commands section" in content
        assert "What, Why, Replaced by, Verification, Source" in content

    def test_verifying_specs_prompts_for_cleanup(self):
        content = _read_skill("verifying-specs")
        assert "Run cleanup-and-refactor now? (yes/no)" in content
        assert "cleanup-and-refactor" in content
        assert "archive-specs" in content

    def test_verifying_specs_handles_no_debt_and_missing_living_specs(self):
        content = _read_skill("verifying-specs")
        lower = content.lower()
        assert "step 4" in lower
        assert "skipped" in lower or "skip" in lower
        assert "warning" in lower


class TestCleanupAndRefactorSkillContent:
    """cleanup-and-refactor must describe the orchestration contract from the specs."""

    def test_cleanup_skill_validates_inputs_and_branch_state(self):
        content = _read_skill("cleanup-and-refactor")
        assert "No technical debt file found for <feature>" in content
        assert "Base branch has uncommitted changes" in content

    def test_cleanup_skill_uses_worktrees_and_updates_status(self):
        content = _read_skill("cleanup-and-refactor")
        assert "cleanup/<feature>" in content
        assert "using-git-worktrees" in content
        assert "_technical-debt.md" in content
        assert "In Progress" in content
        assert "Completed" in content
        assert "Failed" in content

    def test_cleanup_skill_dispatches_code_simplification(self):
        content = _read_skill("cleanup-and-refactor")
        assert "Use superpowerwithcodex:code-simplification" in content
        assert "Technical debt file: docs/specs/<feature>/technical-debt.md" in content
        assert "Implementation directory: src/" in content
        assert "Tests directory: tests/" in content

    def test_cleanup_skill_runs_verification_and_merge_options(self):
        content = _read_skill("cleanup-and-refactor")
        assert "Build command from technical-debt.md" in content
        assert "Test command from technical-debt.md" in content
        assert "Choose merge strategy" in content
        assert "A) Auto-merge to main" in content
        assert "B) Create PR for review" in content
        assert "C) Manual review - show diff" in content
        assert "D) Abort - keep worktree" in content

    def test_cleanup_skill_handles_verification_failures_and_existing_worktree(self):
        content = _read_skill("cleanup-and-refactor")
        assert "Retry verification" in content
        assert "Manual fix (show worktree path)" in content
        assert "Worktree already exists. Delete and retry? (yes/no)" in content
        assert "creating a PR instead" in content or "Fall back to creating a PR" in content


class TestCodeSimplificationSkillContent:
    """code-simplification must describe the three-phase execution workflow."""

    def test_code_simplification_parses_technical_debt_file(self):
        content = _read_skill("code-simplification")
        assert "technical-debt.md" in content
        assert "Build command" in content
        assert "Test command" in content
        assert "What" in content
        assert "Why" in content
        assert "Replaced by" in content
        assert "Verification" in content
        assert "Source" in content

    def test_code_simplification_phase_one_tracks_progress_and_stops_on_failure(self):
        content = _read_skill("code-simplification")
        assert "debt-removal-progress.md" in content
        assert "Remove DEBT-N: <why>" in content
        assert "stop and return" in content.lower()
        assert "Build output is captured" in content
        assert "Test output is captured" in content

    def test_code_simplification_phase_two_limits_scope_and_reports_findings(self):
        content = _read_skill("code-simplification")
        assert "static-analysis-report.md" in content
        assert "Files mentioned in technical-debt.md \"What\" fields" in content
        assert "Files modified during Phase 1" in content
        assert "unused imports" in content.lower()
        assert "unused functions" in content.lower()
        assert "unused classes" in content.lower()

    def test_code_simplification_phase_three_refactors_and_continues_after_failures(self):
        content = _read_skill("code-simplification")
        assert "refactor-progress.md" in content
        assert "Extract duplicate: <function_name>" in content
        assert "Reduce complexity in <function_name>" in content
        assert "Apply <pattern> to <component>" in content
        assert "reverted and skipped" in content.lower()
        assert "Subsequent refactorings are attempted" in content

    def test_code_simplification_returns_summary_to_claude(self):
        content = _read_skill("code-simplification")
        assert "Completed:" in content
        assert "Removed N debt items" in content
        assert "Static analysis: Y unused items removed" in content
        assert "Refactored: Z improvements applied" in content


class TestTechnicalDebtWorkflowWiring:
    """Existing skills should reference the new workflow where appropriate."""

    def test_verifying_specs_points_to_cleanup(self):
        content = _read_skill("verifying-specs")
        assert "cleanup-and-refactor" in content

    def test_cleanup_points_to_code_simplification(self):
        content = _read_skill("cleanup-and-refactor")
        assert "code-simplification" in content

    def test_cleanup_mentions_using_git_worktrees_pattern(self):
        content = _read_skill("cleanup-and-refactor")
        assert "using-git-worktrees" in content
