#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/paradox.js.stub" "$SCRIPT_DIR/src/paradox.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: exhaustion stub restored"
