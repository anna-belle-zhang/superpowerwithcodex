#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/src/server.js.stub" "$SCRIPT_DIR/src/server.js"
rm -f "$SCRIPT_DIR/run.log"
echo "Reset complete: e2e-retry stub restored"
