#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/calculator.js.stub" "$SCRIPT_DIR/src/calculator.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: unit-retry stub restored"
