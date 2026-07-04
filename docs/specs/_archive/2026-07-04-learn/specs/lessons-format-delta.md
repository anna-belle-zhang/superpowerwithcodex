# Lessons Format Delta Spec

New artifact format for `docs/lessons.md` / `~/.claude/lessons-common.md` and
its validator `scripts/validate_lessons.py`, with convention tests in
`tests/structured-specs-integration/`.

## ADDED

### Lesson Entry Shape
GIVEN a confirmed lesson
WHEN it is written to a lessons file
THEN the entry has a `## [tag: <kebab-case-tag>] <Title>` heading and Symptom, Root cause, Correct approach, Occurrences, and Level fields

### Validator Accepts a Well-Formed Lessons File
GIVEN a lessons file whose entries all have valid headings and all five required fields
WHEN validate_lessons.py runs on it
THEN it passes

### Validator Rejects a Missing Field
GIVEN a lessons entry missing one of Symptom, Root cause, Correct approach, Occurrences, or Level
WHEN validate_lessons.py runs on the file
THEN it reports an error naming the entry's tag and the missing field

### Validator Rejects a Malformed Tag
GIVEN an entry heading without a `[tag: ...]` key or with an empty tag
WHEN validate_lessons.py runs on the file
THEN it reports an error identifying the heading and the tag requirement

### Validator Rejects an Invalid Level
GIVEN an entry whose Level is neither `lesson` nor `pattern`
WHEN validate_lessons.py runs on the file
THEN it reports an error naming the entry's tag and the allowed values

### Validator Rejects Duplicate Tags
GIVEN a lessons file containing two entries with the same tag
WHEN validate_lessons.py runs on the file
THEN it reports an error naming the duplicated tag — occurrences of the same lesson belong on one entry's Occurrences line

### Validator Flags Promotion Inconsistency
GIVEN an entry with fewer than 2 occurrences whose Level is `pattern`
WHEN validate_lessons.py runs on the file
THEN it reports an error stating the occurrence count required for pattern level

### Occurrences Carry Date and Project
GIVEN an entry's Occurrences line
WHEN validate_lessons.py parses it
THEN each occurrence has a YYYY-MM-DD date, and an entry with an undated occurrence fails validation with a named error

### Missing File Is Not an Error
GIVEN docs/lessons.md does not exist in a project
WHEN validate_lessons.py runs against that path
THEN it exits successfully, since the lessons file is created lazily on first confirmed write
