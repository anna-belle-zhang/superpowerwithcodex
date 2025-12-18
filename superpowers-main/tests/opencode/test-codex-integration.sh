#!/usr/bin/env bash
# Test: Codex Integration Library
# Tests the codex-integration.js library functions directly via Node.js
# Does not require OpenCode - tests pure library functionality
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Codex Integration Library ==="

source "$SCRIPT_DIR/setup.sh"
trap cleanup_test_env EXIT

LIB_PATH="$HOME/.config/opencode/superpowers/lib/codex-integration.js"

echo "Test 1: Checking codex-integration.js exists..."
if [ -f "$LIB_PATH" ]; then
    echo "  [PASS] codex-integration.js exists"
else
    echo "  [FAIL] codex-integration.js not found at $LIB_PATH"
    exit 1
fi

echo ""
echo "Test 2: checkCodexAvailability returns unavailable when .mcp.json missing..."
no_config_dir="$TEST_HOME/no-mcp-config"
mkdir -p "$no_config_dir"

result=$(cd "$no_config_dir" && node -e "
const codex = require('$LIB_PATH');
(async () => {
  const res = await codex.checkCodexAvailability();
  console.log(JSON.stringify(res));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q '"available":false'; then
    echo "  [PASS] reports available=false"
else
    echo "  [FAIL] did not report available=false"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -q '"error":"'; then
    echo "  [PASS] includes an error message"
else
    echo "  [FAIL] missing error message"
    echo "  Result: $result"
    exit 1
fi

echo ""
echo "Test 3: checkCodexAvailability returns a structured result when configured..."
with_config_dir="$TEST_HOME/with-mcp-config"
mkdir -p "$with_config_dir"
cat > "$with_config_dir/.mcp.json" <<'EOF'
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

result=$(cd "$with_config_dir" && node -e "
const codex = require('$LIB_PATH');
(async () => {
  const res = await codex.checkCodexAvailability();
  console.log(JSON.stringify(res));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q '"available":'; then
    echo "  [PASS] includes available boolean"
else
    echo "  [FAIL] missing available"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -q '"available":false'; then
    if echo "$result" | grep -q '"error":"'; then
        echo "  [PASS] unavailable includes error"
    else
        echo "  [FAIL] unavailable missing error"
        echo "  Result: $result"
        exit 1
    fi
else
    echo "  [PASS] available=true (Codex CLI present)"
fi

echo ""
echo "Test 4: executeWithCodex succeeds and reports attempts..."
result=$(node -e "
const codex = require('$LIB_PATH');
(async () => {
  const res = await codex.executeWithCodex({ prompt: 'Create hello.txt', workingDir: process.cwd(), retryCount: 2 });
  console.log(JSON.stringify(res));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q '"success":true'; then
    echo "  [PASS] success=true"
else
    echo "  [FAIL] expected success=true"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -q '"attempts":1'; then
    echo "  [PASS] attempts=1 on first success"
else
    echo "  [FAIL] expected attempts=1"
    echo "  Result: $result"
    exit 1
fi

echo ""
echo "Test 5: executeWithCodex respects retryCount on simulated failure..."
result=$(node -e "
const codex = require('$LIB_PATH');
(async () => {
  const res = await codex.executeWithCodex({ prompt: 'Invalid task that will fail', workingDir: process.cwd(), retryCount: 2 });
  console.log(JSON.stringify(res));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q '"success":false'; then
    echo "  [PASS] success=false on simulated failure"
else
    echo "  [FAIL] expected success=false"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -q '"attempts":3'; then
    echo "  [PASS] attempts=3 (initial + 2 retries)"
else
    echo "  [FAIL] expected attempts=3"
    echo "  Result: $result"
    exit 1
fi

echo ""
echo "Test 6: retryWithFeedback formats attempt prompts..."
result=$(node -e "
const codex = require('$LIB_PATH');
(async () => {
  const r1 = await codex.retryWithFeedback('Implement feature X', { failure_type: 'test_failure', test_output: 'Expected 5, got 3' }, 1, 2);
  const r2 = await codex.retryWithFeedback('Implement API call', { failure_type: 'test_failure', test_output: 'TypeError: Invalid parameter' }, 2, 2);
  const r3 = await codex.retryWithFeedback('task', {}, 3, 2);
  console.log(JSON.stringify({ r1, r2, r3 }));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q 'Expected 5, got 3'; then
    echo "  [PASS] includes test output on attempt 1"
else
    echo "  [FAIL] missing test output on attempt 1"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -qi 'research required'; then
    echo "  [PASS] includes research guidance on attempt 2"
else
    echo "  [FAIL] missing research guidance on attempt 2"
    echo "  Result: $result"
    exit 1
fi

if echo "$result" | grep -q '"shouldEscalate":true'; then
    echo "  [PASS] escalates when attempts exceed max retries"
else
    echo "  [FAIL] missing shouldEscalate=true for exceeded retries"
    echo "  Result: $result"
    exit 1
fi

echo ""
echo "Test 7: detectBoundaryViolations flags read-only changes..."
result=$(node -e "
const codex = require('$LIB_PATH');
(async () => {
  const boundaries = { implement_in: ['src/service.js'], read_only: ['src/service.test.js', 'package.json'] };
  const changedFiles = ['src/service.js', 'src/service.test.js'];
  const violations = await codex.detectBoundaryViolations(changedFiles, boundaries);
  console.log(JSON.stringify(violations));
})().catch(err => {
  console.error(err);
  process.exit(1);
});
" 2>&1)

if echo "$result" | grep -q 'src/service.test.js'; then
    echo "  [PASS] reports violation file"
else
    echo "  [FAIL] expected src/service.test.js violation"
    echo "  Result: $result"
    exit 1
fi

echo ""
echo "=== All codex integration library tests passed ==="

