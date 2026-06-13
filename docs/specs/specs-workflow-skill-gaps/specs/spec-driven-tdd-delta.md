# Spec-Driven-TDD Skill Delta Spec

No living spec exists for this component; all behaviors are ADDED.

## ADDED

### Compromise Annotated At Creation Time
GIVEN Codex makes a compromise while implementing a task (coverage shortcut, mocked path that should be live, or deferred edge case)
WHEN the task is completed
THEN a `DEBT:` comment exists at the code site using the file's native comment syntax (`# DEBT:` Python, `// DEBT:` JS/Java, `-- DEBT:` SQL)
AND the compromise is listed under `## Issues` in `docs/specs/<feature>/progress.md`

### TDD Loop Includes Debt Annotation Step
GIVEN the file `skills/spec-driven-tdd/SKILL.md`
WHEN its Step 3 TDD loop list is inspected
THEN it contains a step requiring `DEBT:` annotation plus an Issues entry for any compromise, placed before the progress.md update step

### Unannotated Compromise Is A Red Flag
GIVEN the file `skills/spec-driven-tdd/SKILL.md`
WHEN its Red Flags list is inspected
THEN it includes making a compromise without a `DEBT:` annotation and Issues entry
