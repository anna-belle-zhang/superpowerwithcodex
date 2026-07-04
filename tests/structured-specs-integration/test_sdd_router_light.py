"""sdd-router and LIGHT workflow integration tests."""

import json
import os
import subprocess

from conftest import REPO_ROOT, SKILLS_DIR, _extract_frontmatter, _read_skill


class TestSddRouterSkill:
    def test_skill_file_exists_with_frontmatter(self):
        skill_path = os.path.join(SKILLS_DIR, "sdd-router", "SKILL.md")
        assert os.path.isfile(skill_path)

        content = _read_skill("sdd-router")
        frontmatter = _extract_frontmatter(content)
        assert frontmatter["name"] == "sdd-router"
        assert frontmatter["description"].startswith("Use when")

    def test_risk_hits_force_full(self):
        content = _read_skill("sdd-router")
        lower = content.lower()
        assert "production systems" in lower
        assert "writes/deletes data" in lower or "writes or deletes data" in lower
        assert "api signature" in lower
        assert "privacy" in lower
        assert "compliance" in lower
        assert "core data" in lower
        assert "risk" in lower
        assert "FULL" in content

    def test_low_and_high_complexity_routes_are_documented(self):
        content = _read_skill("sdd-router")
        assert "config change" in content
        assert "bugfix" in content
        assert "single-file" in content or "single file" in content
        assert "LIGHT" in content
        assert "new module" in content
        assert "multiple files" in content or "multi-file" in content
        assert "frontend/backend" in content

    def test_uncertainty_escalates_and_user_choice_is_final(self):
        content = _read_skill("sdd-router")
        assert "uncertain" in content.lower() or "ambiguous" in content.lower()
        assert "escalate" in content.lower()
        assert "confirm" in content.lower()
        assert "override" in content.lower()
        assert "user's choice is final" in content or "user choice is final" in content.lower()

    def test_override_does_not_silence_risk(self):
        content = _read_skill("sdd-router")
        lower = content.lower()
        assert "risk hit recommended full" in lower
        assert "overrides to light" in lower or "override" in lower and "light" in lower
        assert "proceed light" in lower
        assert "keep the risk hit visible in the conversation" in lower
        assert "out of scope" in lower
        assert "notes" in lower

    def test_context_restore_reads_latest_without_fabrication(self):
        content = _read_skill("sdd-router")
        assert "docs/handovers/LATEST.md" in content
        assert "read" in content.lower()
        assert "fabricat" in content.lower()

    def test_light_route_writes_mini_spec_then_dispatches_codex(self):
        content = _read_skill("sdd-router")
        assert "docs/specs/<feature>/mini.md" in content
        assert "2-5" in content or "2 to 5" in content
        assert "GIVEN/WHEN/THEN" in content
        assert "approval" in content.lower()
        assert "Use superpowerwithcodex:spec-driven-tdd" in content
        assert "Spec directory: docs/specs/<feature>/" in content

    def test_full_route_delegates_existing_chain_and_no_zero_spec_channel(self):
        content = _read_skill("sdd-router")
        assert "brainstorm" in content
        assert "write-specs" in content
        assert "spec-driven-tdd" in content
        assert "zero-spec" in content.lower() or "no route skips scenarios" in content.lower()
        assert "urgent" in content.lower()


class TestPromptSubmitHookRouterRules:
    def hook_context(self):
        script_path = os.path.join(REPO_ROOT, "hooks", "prompt-submit.sh")
        result = subprocess.run(
            ["bash", script_path],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_specs_before_code_rule_is_tiered_by_router(self):
        context = self.hook_context()
        assert "sdd-router" in context
        assert "FULL = proposal/design/deltas" in context
        assert "LIGHT = mini.md" in context
        assert "risk hit forces FULL" in context or "any risk hit forces FULL" in context
        assert "Never write implementation code without" in context

    def test_router_is_entry_point_and_full_path_commands_remain(self):
        context = self.hook_context()
        router_pos = context.find("sdd-router")
        brainstorm_pos = context.find("brainstorm")
        assert router_pos != -1
        assert brainstorm_pos != -1
        assert router_pos < brainstorm_pos
        assert "write-specs" in context
        assert "verify-specs" in context
        assert "archive-specs" in context

    def test_dispatch_and_verification_rules_keep_existing_meaning(self):
        context = self.hook_context()
        assert "Use superpowerwithcodex:spec-driven-tdd" in context
        assert "Spec directory: docs/specs/<feature>/" in context
        assert "CLAUDE NEVER WRITES UNIT/INTEGRATION TESTS" in context
        assert "VERIFICATION BEFORE CLAIMING DONE" in context
