# Verifying Specs - Living Spec

## Behaviors

### Collect manual debt annotations
GIVEN the codebase contains `// DEBT:` comments in source files
WHEN verify-specs runs Step 4a (debt identification)
THEN all `// DEBT:` comments are collected with file path, line number, and reason

*Added: 2026-03-12 via technical-debt-cleanup*

### Scenario-driven debt identification
GIVEN `docs/specs/_living/` contains existing system behaviors
AND delta specs contain REMOVED sections
WHEN verify-specs runs Step 4b (scenario-driven analysis)
THEN all living scenarios that match REMOVED sections are identified as technical debt

*Added: 2026-03-12 via technical-debt-cleanup*

### Write feature-level technical debt file
GIVEN debt items are identified from manual annotations or scenario-driven analysis
AND build/test commands are known or prompted from user
WHEN verify-specs runs Step 4c
THEN `docs/specs/<feature>/technical-debt.md` is created with:
- Build Commands section (build command, test command)
- Technical Debt section with structured entries (What, Why, Replaced by, Verification, Source)

*Added: 2026-03-12 via technical-debt-cleanup*

### Update project-level debt tracker
GIVEN feature-level technical-debt.md exists
WHEN verify-specs runs Step 4d
THEN `docs/specs/_technical-debt.md` is created or updated with:
- New entries for each debt item
- Unique DEBT-N IDs
- Status set to "Pending"
- Feature name, file paths, and priority fields

*Added: 2026-03-12 via technical-debt-cleanup*

### Prompt user for cleanup
GIVEN N debt items are identified (N > 0)
WHEN verify-specs completes Step 4e
THEN user is prompted: "Found N debt items. Run cleanup-and-refactor now? (yes/no)"
- If yes: invoke cleanup-and-refactor skill
- If no: continue to archive-specs (debt tracked for later)

*Added: 2026-03-12 via technical-debt-cleanup*

### Skip debt identification when no debt found
GIVEN no `// DEBT:` comments exist
AND no REMOVED sections in delta specs
WHEN verify-specs runs Step 4
THEN Step 4 is skipped, no technical-debt.md created, continue to archive-specs

*Added: 2026-03-12 via technical-debt-cleanup*

### Handle missing living specs gracefully
GIVEN `docs/specs/_living/` directory does not exist
WHEN verify-specs runs Step 4b (scenario-driven analysis)
THEN a warning is logged but execution continues (feature may not modify existing behavior)

*Added: 2026-03-12 via technical-debt-cleanup*
