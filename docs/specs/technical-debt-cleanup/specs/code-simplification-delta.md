# Code Simplification Delta Spec

## ADDED

### Read and parse technical debt file
GIVEN Codex is dispatched with technical-debt.md path
WHEN code-simplification activates
THEN it reads the file and extracts:
- Build command
- Test command
- List of all DEBT-N entries with What/Why/Replaced by/Verification/Source fields

### Remove debt item and test
GIVEN Phase 1 (debt removal) is running
AND a DEBT-N entry specifies files to remove
WHEN the skill processes that entry
THEN:
1. Files specified in "What" field are deleted
2. Build command is executed
3. Test command is executed
4. If tests pass: mark done in `debt-removal-progress.md`, commit with message "Remove DEBT-N: <why>"
5. If tests fail: document issue in `debt-removal-progress.md`, stop and return

### Handle build failure during debt removal
GIVEN a debt item is removed
AND build command fails
WHEN the skill handles the error
THEN:
- Build output is captured in `debt-removal-progress.md` under Issues section
- Status for that debt item is marked as failed
- Skill stops and returns (does not continue to next debt item)

### Handle test failure during debt removal
GIVEN a debt item is removed
AND tests fail
WHEN the skill handles the error
THEN:
- Test output is captured in `debt-removal-progress.md` under Issues section
- Status for that debt item is marked as failed
- Skill stops and returns (does not continue to next debt item)

### Determine static analysis scope
GIVEN Phase 2 (static analysis) starts
AND all debt items are successfully removed
WHEN the skill determines which files to analyze
THEN the scope includes only:
- Files mentioned in technical-debt.md "What" fields
- Files modified during Phase 1 (debt removal)

### Scan for unused imports
GIVEN Phase 2 (static analysis) is running
AND the analysis scope is determined (feature-scoped only)
WHEN the skill scans for unused code
THEN unused imports are identified in scoped files only and listed in `static-analysis-report.md`

### Scan for unused functions
GIVEN Phase 2 (static analysis) is running
AND the scope is limited to feature-touched files
WHEN the skill scans for unused code
THEN functions in scoped files that are not referenced anywhere in the codebase are identified and listed in `static-analysis-report.md`

### Scan for unused classes
GIVEN Phase 2 (static analysis) is running
AND the scope is limited to feature-touched files
WHEN the skill scans for unused code
THEN classes in scoped files that are not instantiated anywhere in the codebase are identified and listed in `static-analysis-report.md`

### Remove safe unused code
GIVEN static analysis identified unused code
AND the unused code is "safe" (not referenced in any file)
WHEN the skill processes removal
THEN:
1. Unused code is removed
2. Build command is executed
3. Test command is executed
4. If tests pass: update `static-analysis-report.md`, commit
5. If tests fail: revert removal, document in report, continue to next item

### Extract duplicate code blocks
GIVEN Phase 3 (refactoring) starts
AND static analysis is complete
WHEN the skill identifies duplicates (3+ lines, 2+ occurrences)
THEN:
1. Extract into shared function
2. Run build command
3. Run test command
4. If tests pass: document in `refactor-progress.md`, commit "Extract duplicate: <function_name>"
5. If tests fail: revert, skip this refactoring, continue to next

### Reduce cyclomatic complexity
GIVEN Phase 3 (refactoring) is running
WHEN the skill finds functions with cyclomatic complexity > 10
THEN:
1. Simplify conditionals or extract subfunctions
2. Run build + test
3. If tests pass: document in `refactor-progress.md`, commit "Reduce complexity in <function_name>"
4. If tests fail: revert, skip, continue

### Apply design patterns
GIVEN Phase 3 (refactoring) is running
AND obvious pattern opportunities exist (strategy, factory, etc.)
WHEN the skill identifies clear value in applying a pattern
THEN:
1. Apply the pattern
2. Run build + test
3. If tests pass: document in `refactor-progress.md`, commit "Apply <pattern> to <component>"
4. If tests fail: revert, skip, continue

### Write debt removal progress file
GIVEN Phase 1 completes or encounters an error
WHEN the skill finalizes progress tracking
THEN `debt-removal-progress.md` is written with:
- Progress section: checklist of debt items with status (done/failed)
- Issues section: any build/test failures with output
- Commits section: list of commit SHAs for successfully removed items

### Write static analysis report
GIVEN Phase 2 completes
WHEN the skill finalizes static analysis
THEN `static-analysis-report.md` is written with:
- Unused imports section (with counts)
- Unused functions section (with file paths and line numbers)
- Unused classes section (with details)
- Summary section (total lines deleted, counts by category)

### Write refactor progress file
GIVEN Phase 3 completes
WHEN the skill finalizes refactoring
THEN `refactor-progress.md` is written with:
- List of refactorings applied
- Each entry includes: type (duplicate/complexity/pattern), location, rationale, commit SHA

### Return summary to Claude
GIVEN all three phases complete (or one fails)
WHEN the skill returns control to Claude
THEN a summary is provided:
```
Completed:
- Removed N debt items (X lines deleted)
- Static analysis: Y unused items removed
- Refactored: Z improvements applied

See progress files:
- debt-removal-progress.md
- static-analysis-report.md
- refactor-progress.md
```

### Stop immediately on debt removal failure
GIVEN a debt item removal causes test failure
WHEN the skill handles the failure
THEN:
- No further debt items are processed
- Static analysis and refactoring phases are skipped
- Skill returns immediately with error details

### Continue refactoring despite individual failures
GIVEN Phase 3 (refactoring) is running
AND one refactoring causes test failure
WHEN the skill handles the failure
THEN:
- That refactoring is reverted and skipped
- Subsequent refactorings are attempted
- Final report includes both successful and skipped refactorings

### Handle build command with compilation
GIVEN technical-debt.md specifies build command like `mvn clean compile`
WHEN the skill executes the build command
THEN compilation is performed before running tests (supports Java/C++/Go/etc.)

### Execute build command before tests
GIVEN any code change is made (debt removal, static analysis, or refactoring)
WHEN the skill validates the change
THEN build command is always executed before test command
