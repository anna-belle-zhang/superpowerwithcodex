#!/usr/bin/env bash
# UserPromptSubmit hook — re-injects specs-first workflow rules every turn.
# Workaround for Claude 4.x instruction-adherence regression where skills/CLAUDE.md
# are read but not followed. Hooks fire at process level, immune to model regression.

set -euo pipefail

RULES='MANDATORY WORKFLOW RULES (enforced every turn — not optional):

1. SPECS BEFORE CODE: Never write implementation code without specs in docs/specs/<feature>/.
   - Brainstorm first → write specs → dispatch Codex with spec path only
   - If asked to "just implement", ask: "Specs first — run /superpowerwithcodex:brainstorm?"

2. DISPATCH FORMAT (never deviate):
   Use superpowerwithcodex:spec-driven-tdd
   Spec directory: docs/specs/<feature>/
   Implement in: src/
   Tests in: tests/
   Test command: <test command>

3. CLAUDE NEVER WRITES UNIT/INTEGRATION TESTS — Codex derives all tests from GIVEN/WHEN/THEN specs.
   Claude only writes E2E tests after Codex returns.

4. SKILL COMMANDS TO USE:
   - /superpowerwithcodex:brainstorm   → before any feature work
   - /superpowerwithcodex:write-specs  → after brainstorming
   - /superpowerwithcodex:verify-specs → after Codex returns
   - /superpowerwithcodex:archive-specs → after verify passes

5. VERIFICATION BEFORE CLAIMING DONE: Run tests and show output. Never say "done" without evidence.'

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

rules_escaped=$(escape_for_json "$RULES")

printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "UserPromptSubmit",\n    "additionalContext": "%s"\n  }\n}\n' "$rules_escaped"

exit 0
