# Archiving-Specs Skill Delta Spec

No living spec exists for this component; all behaviors are ADDED.

## ADDED

### System Index Updated On Archive
GIVEN `docs/specs/_living/ARCHITECTURE.md` exists
AND a feature's living specs were created or updated during the merge step
WHEN archiving-specs runs the index-update step (Step 2.5)
THEN every created or updated living spec has an index entry with component name, a markdown link, and a 1-3 line behavior summary
AND the index header's "as of" date is updated to today

### Unindexed Living Spec Detected
GIVEN a file exists in `docs/specs/_living/` (other than ARCHITECTURE.md) that ARCHITECTURE.md does not reference
WHEN the index verification check runs
THEN the check reports the file as not indexed

### Missing Index Tolerated
GIVEN `docs/specs/_living/ARCHITECTURE.md` does not exist
WHEN archiving-specs runs
THEN the index-update step is skipped without failure
AND creating the index may be offered once three or more living specs exist

### Missing Progress.md Blocks Archive
GIVEN the feature directory has no `progress.md`
WHEN the pre-archive completeness check (Step 2.6) runs
THEN archiving STOPs and asks whether to backfill a stub or proceed with a noted gap

### Missing Proposal Or Design Warns Without Blocking
GIVEN the feature directory is missing `proposal.md` or `design.md`
WHEN the pre-archive completeness check runs
THEN a warning is issued and archiving continues

### Stray Spec Files Relocated Before Archive
GIVEN a delta or spec `*.md` file sits at the feature root instead of in `specs/`
WHEN the pre-archive completeness check runs
THEN the file is moved into `specs/` before the directory is archived

### Junk Files Removed Before Archive
GIVEN the feature directory contains junk files (`* copy.*` or editor backups)
WHEN the pre-archive completeness check runs
THEN the junk files are deleted before the directory is archived

### Overview Lists Six Steps Including Index Update
GIVEN the file `skills/archiving-specs/SKILL.md`
WHEN its Overview numbered list is inspected
THEN it lists six steps, including updating the system index before the archive move

### Cross-References Use A Consistent Resolvable Namespace
GIVEN the file `skills/archiving-specs/SKILL.md`
WHEN all skill cross-references in it are inspected
THEN every reference uses one consistent namespace that the installed plugin resolves
