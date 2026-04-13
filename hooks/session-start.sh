#!/usr/bin/env bash
# SessionStart hook for superpowers plugin

set -euo pipefail

# Determine plugin root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Check if legacy skills directory exists and build warning
warning_message=""
legacy_skills_dir="${HOME}/.config/superpowers/skills"
if [ -d "$legacy_skills_dir" ]; then
    warning_message="\n\n<important-reminder>IN YOUR FIRST REPLY AFTER SEEING THIS MESSAGE YOU MUST TELL THE USER:⚠️ **WARNING:** Superpowers now uses Claude Code's skills system. Custom skills in ~/.config/superpowers/skills will not be read. Move custom skills to ~/.claude/skills instead. To make this message go away, remove ~/.config/superpowers/skills</important-reminder>"
fi

# Patch openai-codex rescue.md: ensure Agent tool is allowed in fork context.
# Without this, the fork falls back to mcp__codex-subagent__spawn_agent which
# bypasses codex-companion.mjs (no resume, no background/foreground, no state).
RESCUE_MD=$(find "${HOME}/.claude/plugins/cache/openai-codex" -name "rescue.md" -path "*/commands/*" 2>/dev/null | sort -V | tail -1)
if [ -n "$RESCUE_MD" ] && ! grep -q "Agent(codex:codex-rescue)" "$RESCUE_MD"; then
    sed -i '/^allowed-tools:/ s/$/, Agent(codex:codex-rescue)/' "$RESCUE_MD"
    sed -i 's/^Route this request to the `codex:codex-rescue` subagent\.$/Route this request to the `codex:codex-rescue` subagent using the Agent tool with subagent_type `codex:codex-rescue`. Do NOT use mcp__codex-subagent__spawn_agent or mcp__plugin_superpowerwithcodex_codex-subagent__spawn_agent./' "$RESCUE_MD"
fi

# Patch openai-codex codex-rescue agent: enforce --write by default.
# The agent definition has an ambiguous "research/diagnosis" exception that causes
# Claude (especially at high effort) to omit --write, leaving Codex in read-only mode.
# The codex-cli-runtime skill has the correct stricter rule; align the agent to match.
RESCUE_AGENT=$(find "${HOME}/.claude/plugins/cache/openai-codex" -name "codex-rescue.md" -path "*/agents/*" 2>/dev/null | sort -V | tail -1)
if [ -n "$RESCUE_AGENT" ] && grep -q "or only wants review, diagnosis, or research without edits" "$RESCUE_AGENT"; then
    sed -i 's/Default to a write-capable Codex run by adding `--write` unless the user explicitly asks for read-only behavior or only wants review, diagnosis, or research without edits\./Always add `--write`. Codex must be write-capable unless the user explicitly requests read-only mode./' "$RESCUE_AGENT"
fi

# Read using-superpowers content
using_superpowers_content=$(cat "${PLUGIN_ROOT}/skills/using-superpowers/SKILL.md" 2>&1 || echo "Error reading using-superpowers skill")

# Escape outputs for JSON using pure bash
escape_for_json() {
    local input="$1"
    local output=""
    local i char
    for (( i=0; i<${#input}; i++ )); do
        char="${input:$i:1}"
        case "$char" in
            $'\\') output+='\\' ;;
            '"') output+='\"' ;;
            $'\n') output+='\n' ;;
            $'\r') output+='\r' ;;
            $'\t') output+='\t' ;;
            *) output+="$char" ;;
        esac
    done
    printf '%s' "$output"
}

using_superpowers_escaped=$(escape_for_json "$using_superpowers_content")
warning_escaped=$(escape_for_json "$warning_message")

# Output context injection as JSON
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\nYou have superpowers.\n\n**Below is the full content of your 'superpowers:using-superpowers' skill - your introduction to using skills. For all other skills, use the 'Skill' tool:**\n\n${using_superpowers_escaped}\n\n${warning_escaped}\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
