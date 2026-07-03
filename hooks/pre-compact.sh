#!/usr/bin/env bash
# PreCompact hook for superpowers plugin

set -euo pipefail

cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreCompact","additionalContext":"Before compaction, use the handover-manager skill to write a handover document at docs/handovers/YYYY-MM-DD-HHmm-<topic>.md. Include decisions, changes this round, a git-verified file list, real verification results, open items, and copy-pasteable restart instructions. Update docs/handovers/LATEST.md before compaction proceeds."}}
EOF

exit 0
