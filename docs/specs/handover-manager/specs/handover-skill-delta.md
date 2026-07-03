# Handover Manager Skill Delta Spec

## ADDED

### Handover Document Generation
GIVEN a work session with decisions made and files changed
WHEN a handover is generated
THEN a document is created at docs/handovers/YYYY-MM-DD-HHmm-<topic>.md containing all six sections: Decisions, Changes this round, File list, Verification results, Open items, Restart instructions

### Git-Verified File List
GIVEN a handover is being generated in a git repository
WHEN the file list section is written
THEN it is derived from git diff --stat and git status output, and files not confirmed by git are not listed

### File List Outside Git
GIVEN a handover is being generated in a directory that is not a git repository
WHEN the file list section is written
THEN the section explicitly states that git verification was unavailable instead of listing files from memory

### LATEST Index Update
GIVEN a new handover document has been written
WHEN generation completes
THEN docs/handovers/LATEST.md is rewritten to point at the new document with its topic and status

### Honest Progress Reporting
GIVEN work in progress where tests fail or a task is half-done
WHEN the verification results section is written
THEN it records the actual test command and its real output summary, including failures, without claiming more progress than occurred

### Executable Restart Instructions
GIVEN a handover is being generated
WHEN the restart instructions section is written
THEN every instruction is a concrete copy-pasteable command or file path, not a vague description

### Tool Switch Trigger
GIVEN the user states work will continue in another tool (Codex, Claude Cowork, or another session)
WHEN the current session prepares to stop
THEN a handover is generated before the switch

### Resume From Handover
GIVEN docs/handovers/LATEST.md exists and points at a valid handover
WHEN the user asks to continue the topic in a fresh session
THEN the agent reads the handover, restores decisions and open items, follows the restart instructions, and does not re-ask settled decisions

### Resume With Broken Index
GIVEN docs/handovers/LATEST.md points at a file that does not exist
WHEN the user asks to continue the topic
THEN the agent falls back to the newest timestamped file in docs/handovers/, uses it, and repairs LATEST.md

### Resume With No Handover
GIVEN no handover documents exist in the project
WHEN the user asks to continue a topic
THEN the agent states that no handover was found and falls back to normal context gathering without fabricating prior state

### Reference Instead of Copy
GIVEN fine-grained ledgers exist for the current work (grill ledger, spec progress.md)
WHEN a handover is generated
THEN the handover references their file paths rather than duplicating their content
