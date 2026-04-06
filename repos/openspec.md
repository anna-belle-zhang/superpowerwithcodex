Based on the current repo's architecture and OpenSpec's strengths:

  ---
  High Value, Low Effort

  1. OpenSpec artifact shape → improve specs-first workflow discoverability
  OpenSpec's default change bundle is explicit and easy to teach: proposal,
  specs, design, tasks, then apply/archive. superpowerwithcodex already has
  a stronger specs-first workflow, but it is spread across `docs/specs/`,
  `docs/plans/`, skill instructions, and progress tracking. Borrowing
  OpenSpec's artifact framing for docs and onboarding would make the existing
  workflow easier to explain without changing the underlying system.

  2. `/opsx:explore` pattern → enhance brainstorming entry
  OpenSpec cleanly separates "explore before committing to a change" from
  "create artifacts". That maps well to the current `brainstorm →
  write-specs/write-plan` flow. A lighter exploratory entry point before
  spec-writing would reduce the tendency to jump into implementation too
  early, especially for vague user requests.

  3. verify/sync/archive terminology → tighten post-implementation flow
  OpenSpec names the endgame clearly: verify implementation, sync specs, then
  archive the change. superpowerwithcodex already has equivalents
  (`verify-specs`, `_living`, `_archive`) but the flow is less unified.
  Adopting the language and checklist shape would make completion easier to
  teach and automate.

  ---
  Moderate Effort, High Value

  4. OpenSpec compatibility bridge → import/export between `openspec/changes`
  and `docs/specs/`
  OpenSpec is gaining adoption as a tool-agnostic spec layer. A bridge skill
  that can ingest an OpenSpec change folder and map it to
  `docs/specs/<feature>/specs/*-delta.md`, `progress.md`, and plan files would
  let superpowerwithcodex interoperate instead of competing head-on. This is
  higher leverage than reimplementing OpenSpec's CLI outright.

  5. Schema/profile concept → reusable workflow presets
  OpenSpec exposes workflow profiles (`core` vs expanded workflows) and schema-
  driven artifact generation. superpowerwithcodex could borrow that idea for
  different operating modes: lightweight bugfix, full spec-driven feature,
  docs-only change, or research spike. That would reduce ceremony mismatch
  across tasks without weakening the disciplined flow.

  ---
  Skip / Already Covered

  - Full OpenSpec adoption as the primary workflow — too much overlap with the
  current `brainstorm → write-specs → spec-driven-tdd → verify-specs`
  pipeline, and it would create two competing artifact systems
  - Rebuilding OpenSpec's CLI inside this repo — lower leverage than selective
  interoperability and terminology improvements
  - Replacing the current spec archive structure with `openspec/changes/` —
  the existing `_living` and `_archive` model is already tailored to this repo

  ---
  Recommended Priority

  1. Use OpenSpec's artifact naming and completion language to sharpen docs and
  onboarding around the existing specs-first workflow
  2. Add an "explore before spec" entry pattern inspired by `/opsx:explore`
  3. Build a bridge skill that can translate OpenSpec change folders into
  superpowerwithcodex spec directories
  4. Consider workflow profiles once the current flow is easier to onboard into
