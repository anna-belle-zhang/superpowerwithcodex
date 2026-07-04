# Learn - Living Spec

`skills/learn/` — lesson → pattern → proposal experience capture.

## Behaviors

### Active Capture Waits for Confirmation
GIVEN the user asks to note a pitfall or lesson
WHEN learn drafts the lesson entry
THEN it shows the complete entry and writes to docs/lessons.md only after the user confirms

*Added: 2026-07-04 via learn*

### Passive Scan Produces Candidates, Not Writes
GIVEN handover-manager's wrap-up invokes the learn scan
WHEN the scan finds signals (user corrected the approach, a debug loop exceeded 2 rounds, a technical decision was made with a stated reason, or the same problem class recurred)
THEN it presents a candidate list for selection and writes nothing until the user confirms specific entries

*Added: 2026-07-04 via learn*

### Confidence Is Not Confirmation
GIVEN learn has drafted an entry it considers obviously correct
WHEN it is about to write to any lessons file
THEN it still shows the entry and waits for explicit user confirmation — certainty never bypasses the gate

*Added: 2026-07-04 via learn*

### Scan With No Signals Reports Empty
GIVEN a session containing none of the scan signals
WHEN the learn scan runs
THEN it states that no lesson candidates were found and does not invent entries to appear useful

*Added: 2026-07-04 via learn*

### Dedup By Tag, Not Title
GIVEN a new lesson whose tag matches an existing entry in docs/lessons.md
WHEN the confirmed entry is recorded
THEN the existing entry gains an occurrence line (date + project) instead of a duplicate entry being appended

*Added: 2026-07-04 via learn*

### Different Root Cause Gets a New Tag
GIVEN a symptom that resembles an existing entry but has a different root cause
WHEN learn drafts the entry
THEN it assigns a distinct tag rather than incrementing the existing tag's occurrences

*Added: 2026-07-04 via learn*

### Promotion to Pattern at Two Occurrences
GIVEN a tag reaches 2 occurrences on a confirmed write
WHEN learn processes the write
THEN it offers to sync the entry to ~/.claude/lessons-common.md with Level: pattern, and syncs only after the user confirms

*Added: 2026-07-04 via learn*

### Upgrade Proposal at Three Occurrences
GIVEN a tag reaches 3 occurrences on a confirmed write
WHEN learn processes the write
THEN it offers to generate an upgrade proposal document naming the target skill, the suggested constraint entry, and the supporting occurrence records

*Added: 2026-07-04 via learn*

### Proposals Never Edit Skills
GIVEN an upgrade proposal has been generated and confirmed
WHEN the user accepts the proposal
THEN learn directs the change through the normal writing-skills process (including pressure testing) and never edits the target skill file itself

*Added: 2026-07-04 via learn*

### Declined Candidate Is Dropped
GIVEN the user declines a drafted entry or scan candidate
WHEN learn continues
THEN the declined item is discarded without being written or re-asked later in the session

*Added: 2026-07-04 via learn*

### Missing Lessons File Is Created
GIVEN docs/lessons.md does not exist
WHEN the first entry is confirmed
THEN learn creates the file with a header and appends the entry

*Added: 2026-07-04 via learn*

### Unwritable Shared File Degrades Gracefully
GIVEN ~/.claude/lessons-common.md cannot be written
WHEN a pattern sync is confirmed
THEN learn reports the failure, keeps the project-level entry intact, and does not retry silently

*Added: 2026-07-04 via learn*
