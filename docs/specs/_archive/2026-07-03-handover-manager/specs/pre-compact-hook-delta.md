# PreCompact Hook Delta Spec

## ADDED

### PreCompact Registration
GIVEN the plugin's hooks/hooks.json
WHEN hook configuration is loaded
THEN a PreCompact entry exists that dispatches pre-compact.sh through run-hook.cmd, alongside the existing SessionStart and UserPromptSubmit entries

### Reminder Injection
GIVEN a session where context compaction is about to run
WHEN the PreCompact hook executes
THEN it emits hookSpecificOutput.additionalContext instructing the agent to write a handover document via the handover-manager skill before compaction proceeds

### Hook Output Validity
GIVEN the pre-compact.sh script
WHEN it runs on a supported platform (Unix bash or Windows Git Bash via run-hook.cmd)
THEN it exits with code 0 and prints a single valid JSON object to stdout

### Non-Blocking Behavior
GIVEN the PreCompact hook fires
WHEN the reminder is injected
THEN compaction itself is not blocked and no exit code 2 is returned
