# Archiving Specs - Living Spec

`skills/archiving-specs/SKILL.md` — delta-to-living merge and feature archiving.

## Behaviors

### Archive Merges Mini-Spec Scenarios Into Living Specs
GIVEN a verified LIGHT feature with mini.md
WHEN archive-specs runs
THEN each mini.md scenario appears in `docs/specs/_living/` with an "Added: YYYY-MM-DD via <feature>" attribution and the feature directory moves to `docs/specs/_archive/YYYY-MM-DD-<feature>/`

*Modified: 2026-07-04 via sdd-router-light (was: archive-specs merged only <component>-delta.md files into living specs)*
