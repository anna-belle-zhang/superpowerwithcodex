# Verifying-Specs Skill Delta Spec

Living spec: `docs/specs/_living/verifying-specs.md`

## ADDED

### Collect Debt From Progress.md Issues
GIVEN `docs/specs/<feature>/progress.md` contains an `## Issues` section with an entry describing a coverage compromise or deferred work
WHEN verify-specs runs Step 4b-2
THEN the entry is collected as a debt candidate with its source noted as progress.md Issues

### Narrative Issues Entries Are Not Debt
GIVEN progress.md `## Issues` contains an entry that merely narrates an event (e.g. "renamed X to Y") with no future work implied
WHEN verify-specs runs Step 4b-2
THEN the entry is not collected as a debt candidate

### Missing Progress.md Tolerated At Verification
GIVEN `docs/specs/<feature>/progress.md` is missing or its `## Issues` section is empty
WHEN verify-specs runs Step 4b-2
THEN verification continues without failure

### Debt Summary Reports Issues-Source Count
GIVEN debt candidates were collected from progress.md Issues
WHEN verify-specs writes the Technical Debt Summary
THEN the summary includes a count of progress.md-Issues debt items

## MODIFIED

### Collect Manual Debt Annotations
**Was:** Step 4a scans only C-style `// DEBT:` comments, so Python `# DEBT:` and SQL `-- DEBT:` annotations are never found
**Now:** Step 4a scans `DEBT:` annotations in every comment syntax in use (`#`, `//`, `--`, `<!--`)
**Reason:** the C-style-only pattern is why the debt pipeline never fired on Python codebases (review finding #2b)

GIVEN the codebase contains `# DEBT:` (Python), `// DEBT:` (JS), and `-- DEBT:` (SQL) comments
WHEN verify-specs runs the Step 4a scan
THEN all three annotations are collected with file path, line number, and reason text

### Skip Debt Identification When No Debt Found
**Was:** Step 4 is skipped when there are no `// DEBT:` comments and no REMOVED delta sections
**Now:** Step 4 is skipped only when there are additionally no debt-bearing progress.md Issues entries
**Reason:** progress.md Issues is now a third debt source and must be checked before declaring no debt

GIVEN no `DEBT:` comments exist in any comment syntax
AND no REMOVED sections exist in delta specs
AND progress.md has no debt-bearing Issues entries
WHEN verify-specs runs Step 4
THEN Step 4 is skipped, no technical-debt.md is created, and flow continues to archiving

### Prompt User For Cleanup
**Was:** SKILL.md Step 4e contains two contradictory "If no:" branches (regression-era editing artifact, commit `91da369`)
**Now:** Step 4e contains exactly one "If no:" branch, routing to archiving-specs with debt tracked for later — matching the living spec, which already states the correct behavior
**Reason:** review finding #7; the skill text contradicted itself, not the intended behavior

GIVEN the file `skills/verifying-specs/SKILL.md`
WHEN its Step 4e branch list is inspected
THEN exactly one "If no:" bullet exists and it routes to archiving-specs with debt tracked for later

### Cross-References Use A Consistent Resolvable Namespace
**Was:** skill cross-references mix `superpowers:` and bare names while the installed plugin namespace is `superpowerwithcodex:`
**Now:** all skill cross-references in the file use the namespace the installed plugin actually resolves
**Reason:** review finding #7 proofread; broken references silently fail at invocation time

GIVEN the file `skills/verifying-specs/SKILL.md`
WHEN all skill cross-references in it are inspected
THEN every reference uses one consistent namespace that the installed plugin resolves
