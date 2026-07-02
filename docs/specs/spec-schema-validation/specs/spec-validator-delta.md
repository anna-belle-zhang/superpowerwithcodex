# Spec Validator Delta Spec

## ADDED

### Valid feature directory passes
GIVEN a feature directory with a proposal.md containing non-empty `## Intent` and `## Scope` sections, a non-empty design.md, and a specs/ directory with one delta file whose ADDED behavior contains GIVEN/WHEN/THEN lines
WHEN `python scripts/validate_specs.py <dir>` is run
THEN the process exits with code 0 and stdout contains a line starting with `OK:` reporting the delta spec count and scenario count

### Missing proposal.md fails
GIVEN a feature directory without a proposal.md
WHEN the validator is run on it
THEN the process exits with code 1 and stdout contains an `ERROR` line naming `proposal.md` and stating it is missing

### Empty Intent section fails
GIVEN a proposal.md whose `## Intent` heading exists but has no content before the next heading
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names `proposal.md` and the empty `Intent` section

### Missing design.md fails
GIVEN a feature directory without a design.md
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names `design.md` as missing

### Missing or empty specs directory fails
GIVEN a feature directory whose specs/ directory is absent or contains no `*-delta.md` files
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line states that no delta specs were found

### Delta file without change sections fails
GIVEN a delta file containing none of `## ADDED`, `## MODIFIED`, `## REMOVED`
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names that delta file and states it has no change sections

### ADDED behavior without complete scenario fails
GIVEN a delta file with an ADDED behavior whose body has a GIVEN line but no THEN line
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names the delta file and the behavior heading and states the scenario is incomplete

### Single-line scenario counts as complete
GIVEN an ADDED behavior whose body contains one line of the form `GIVEN x WHEN y THEN z`
WHEN the validator is run
THEN that behavior produces no error

### MODIFIED behavior requires Was Now Reason and scenario
GIVEN a delta file with a MODIFIED behavior that has GIVEN/WHEN/THEN lines but is missing the `**Reason:**` field
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names the behavior and the missing `Reason` field

### REMOVED behavior requires Was and Reason
GIVEN a delta file with a REMOVED behavior missing its `**Was:**` field
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names the behavior and the missing `Was` field

### Behavior in both MODIFIED and REMOVED fails
GIVEN a feature whose delta files contain the same behavior heading (case-insensitive, trimmed) under `## MODIFIED` in one place and `## REMOVED` in another
WHEN the validator is run
THEN the process exits with code 1 and an `ERROR` line names the behavior and states it appears in both MODIFIED and REMOVED

### All violations reported in one run
GIVEN a feature directory with a missing design.md and a delta file with an incomplete ADDED scenario
WHEN the validator is run
THEN stdout contains an `ERROR` line for each of the two violations and the process exits with code 1

### Usage errors exit 2
GIVEN a path that does not exist, or a path ending in `_living` or `_archive`, or no argument at all
WHEN the validator is invoked that way
THEN the process exits with code 2 and prints a usage message to stderr

### Non-delta files in specs directory are ignored
GIVEN a specs/ directory containing a valid delta file and an extra `notes.md`
WHEN the validator is run
THEN `notes.md` produces no errors and is not counted as a delta spec
