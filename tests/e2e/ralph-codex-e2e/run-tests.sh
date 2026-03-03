#!/bin/bash
# Ralph-Codex-E2E integration test runner
# Usage: bash run-tests.sh
# Requires: Ralph Wiggum plugin, Codex MCP configured, ~/.codex/config.toml with network_access=true

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0
RESULTS=()

check_prerequisites() {
  echo "Checking prerequisites..."
  if ! command -v codex &>/dev/null; then
    echo "ERROR: codex CLI not found. Install via: pip install codex-cli"
    exit 1
  fi
  if [ ! -f "$HOME/.codex/config.toml" ]; then
    echo "WARNING: ~/.codex/config.toml not found. Integration tests may fail."
  fi
  echo "Prerequisites OK"
}

run_scenario() {
  local name=$1
  local dir="$SCRIPT_DIR/$name"
  local expected="$dir/expected-outcome.md"
  local log="$dir/run.log"

  echo ""
  echo "========================================"
  echo "Scenario: $name"
  echo "========================================"

  # Reset to baseline
  bash "$dir/reset.sh"

  # Record baseline git state
  local baseline_hash
  baseline_hash=$(git -C "$SCRIPT_DIR" rev-parse HEAD)

  # Run ralph-codex-e2e against this toy project
  # NOTE: This must be invoked manually in a Claude Code session:
  #   /ralph-loop "Execute plan: tests/e2e/ralph-codex-e2e/$name/plan.md ..." --max-iterations 10
  # This runner verifies pre/post conditions only.

  echo "Pre-condition check: verifying stub fails tests..."
  local test_result=0
  (cd "$dir" && npm test 2>&1 || true) | grep -q "FAIL\|not implemented\|Not implemented\|Error" && test_result=1 || test_result=0

  if [ "$test_result" -eq 1 ]; then
    echo "  PRE-CONDITION PASS: stub correctly fails tests"
  else
    echo "  PRE-CONDITION FAIL: stub should fail tests but doesn't"
    RESULTS+=("FAIL (pre-condition): $name")
    ((FAIL++))
    return
  fi

  # Verify reset.sh works
  echo "Verifying reset.sh..."
  if bash "$dir/reset.sh" 2>&1 | grep -q "Reset complete"; then
    echo "  RESET PASS: reset.sh outputs expected message"
  else
    echo "  RESET FAIL: reset.sh did not output 'Reset complete'"
    RESULTS+=("FAIL (reset): $name")
    ((FAIL++))
    return
  fi

  echo ""
  echo "  Infrastructure verified for: $name"
  echo "  To run full scenario: invoke ralph-codex-e2e against $dir/plan.md"
  echo "  Expected outcomes documented in: $expected"

  RESULTS+=("PASS (pre-conditions): $name")
  ((PASS++))
}

check_prerequisites

run_scenario "happy-path"
run_scenario "unit-retry"
run_scenario "e2e-retry"
run_scenario "exhaustion"

echo ""
echo "========================================"
echo "RESULTS"
echo "========================================"
for r in "${RESULTS[@]}"; do
  echo "  $r"
done
echo ""
echo "Passed: $PASS / $((PASS + FAIL))"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
