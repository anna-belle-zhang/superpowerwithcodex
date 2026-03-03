#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/src/greet.js.stub" "$SCRIPT_DIR/src/greet.js"
echo "Reset complete: happy-path stub restored"
