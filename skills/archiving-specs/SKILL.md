---
name: archiving-specs
description: Use when specs are verified and work is merging - merges delta specs into living specs and archives feature spec directory with change history
---

# Archiving Specifications

Merge verified delta specs into living specifications and archive the feature directory.

**Core principle:** Living specs are the single source of truth for current system behavior.

**Announce at start:** "I'm using the archiving-specs skill to archive specifications."

## Overview

Post-completion merge flow:
1. ADDED scenarios → append to living spec
2. MODIFIED scenarios → replace in living spec
3. REMOVED scenarios → delete from living spec + record in change history
4. Update system index (`docs/specs/_living/ARCHITECTURE.md`)
5. Move feature directory to archive
6. Commit

## Prerequisites

- `superpowerwithcodex:verifying-specs` must have passed (all checks PASS)
- If verification hasn't been run, run it first. Do not archive unverified specs.

## The Process

### Step 1: Locate Specs and Living Directory

```bash
# Feature specs
ls docs/specs/<feature>/specs/*-delta.md

# Living specs (create if first time)
mkdir -p docs/specs/_living
```

### Step 2: Process Each Delta Spec

For each `<component>-delta.md`:

#### ADDED Entries

- Check if `docs/specs/_living/<component>.md` exists
- If yes: append the new scenarios under the appropriate section
- If no: create `docs/specs/_living/<component>.md` with the new scenarios

```markdown
# <Component Name> - Living Spec

## Behaviors

### <Behavior Name>
GIVEN [precondition]
WHEN [action]
THEN [expected result]

*Added: YYYY-MM-DD via <feature>*
```

#### MODIFIED Entries

- Find the matching behavior in `docs/specs/_living/<component>.md`
- Replace the old scenario with the new one
- Add a change history entry

```markdown
### <Behavior Name>
GIVEN [precondition]
WHEN [action]
THEN [new expected result]

*Modified: YYYY-MM-DD via <feature> (was: [brief old behavior])*
```

#### REMOVED Entries

- Find the matching behavior in `docs/specs/_living/<component>.md`
- Delete the scenario section
- Add to change history at the bottom of the living spec

```markdown
## Change History

- YYYY-MM-DD: Removed "<Behavior Name>" via <feature> (reason: [reason from delta])
```

### Step 2.5: Update System Index

After processing all delta specs, update `docs/specs/_living/ARCHITECTURE.md`:

1. If `docs/specs/_living/ARCHITECTURE.md` does not exist:
   - Skip this step without failure
   - If three or more living specs now exist, offer to create `ARCHITECTURE.md` once
2. For each living spec created or updated in Step 2:
   - Add or update an entry with: component name, a markdown link to the file, and a 1–3 line behavior summary
   - Update the index header's "as of" date to today
3. **Index verification check:** Scan `docs/specs/_living/` for any `.md` file (excluding `ARCHITECTURE.md`) that `ARCHITECTURE.md` does not reference — report each unindexed file as not indexed

### Step 2.6: Pre-Archive Completeness Check

Before moving the feature directory, verify it is complete:

1. **progress.md** — if the feature directory has no `progress.md`, STOP and ask whether to backfill a stub or proceed with a noted gap
2. **proposal.md / design.md** — if either is missing, issue a warning and continue (not blocking)
3. **Stray spec files** — if any `*.md` file sits at the feature root instead of inside `specs/`, move it into `specs/` before archiving
4. **Junk files** — if the feature directory contains junk files (`* copy.*` or editor backups), delete them before archiving

### Step 3: Archive Feature Directory

```bash
mkdir -p docs/specs/_archive
mv docs/specs/<feature> docs/specs/_archive/YYYY-MM-DD-<feature>
```

### Step 4: Commit

```bash
git add docs/specs/_living/ docs/specs/_archive/
git commit -m "spec: archive <feature> specs into living documentation"
```

### Step 5: Report

```markdown
## Archiving Complete

**Feature:** <feature>
**Archived to:** docs/specs/_archive/YYYY-MM-DD-<feature>/

**Living specs updated:**
- <component>.md: N added, M modified, K removed

**Change history entries:** K
```

## Living Spec Format

Each living spec file follows this structure:

```markdown
# <Component Name> - Living Spec

## Behaviors

### <Behavior 1>
GIVEN ...
WHEN ...
THEN ...

*Added: YYYY-MM-DD via <feature>*

### <Behavior 2>
GIVEN ...
WHEN ...
THEN ...

*Modified: YYYY-MM-DD via <feature> (was: [old behavior])*

## Change History

- YYYY-MM-DD: Removed "<Old Behavior>" via <feature> (reason: ...)
- YYYY-MM-DD: Removed "<Another>" via <other-feature> (reason: ...)
```

## Key Principles

- **Verify before archiving** — never archive unverified specs
- **Living specs are truth** — they reflect the current system, not history
- **Change history preserves context** — removed behaviors still have a record
- **One component per file** — mirrors delta spec organization
- **Idempotent** — running archive twice on the same feature should be safe (second run is a no-op if already archived)

## Integration

**Called by:**
- `superpowerwithcodex:finishing-a-development-branch` — after merge/PR
- `superpowerwithcodex:ralph-codex-e2e` — post-loop after verification

**Requires:**
- Verified specs (`superpowerwithcodex:verifying-specs` passed)
- Delta specs in `docs/specs/<feature>/specs/`

**Produces:**
- Updated living specs in `docs/specs/_living/`
- Archived feature in `docs/specs/_archive/YYYY-MM-DD-<feature>/`
