#!/usr/bin/env bash
# Test: Codex MCP Integration (Smoke)
# Best-effort environment check for Codex MCP configuration.
# This does not attempt full MCP protocol calls (no JS MCP client is bundled here).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Codex MCP Integration (Smoke) ==="

source "$SCRIPT_DIR/setup.sh"
trap cleanup_test_env EXIT

LIB_PATH="$HOME/.config/opencode/superpowers/lib/codex-integration.js"

if ! command -v codex >/dev/null 2>&1; then
    echo "  [SKIP] codex CLI not found on PATH"
    exit 0
fi

test_dir="$TEST_HOME/codex-mcp-smoke"
mkdir -p "$test_dir"

cat > "$test_dir/.mcp.json" <<'EOF'
{
  "mcpServers": {
    "codex-subagent": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}
EOF

result=$(cd "$test_dir" && node -e "
const codex = require('$LIB_PATH');
(async () => {
  const status = await codex.checkCodexAvailability();
  console.log(JSON.stringify(status));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q '"available":true'; then
    echo "  [PASS] Codex availability check passes"
    exit 0
fi

if echo "$result" | grep -q '"available":false'; then
    echo "  [SKIP] Codex reported unavailable: $result"
    exit 0
fi

echo "  [FAIL] Unexpected output: $result"
exit 1

