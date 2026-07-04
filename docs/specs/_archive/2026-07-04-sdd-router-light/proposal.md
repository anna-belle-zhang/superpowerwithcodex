# sdd-router + LIGHT Channel Proposal

## Intent

Every request currently pays the FULL spec cost (brainstorm → proposal/design/deltas
→ Codex) because the prompt-submit hook mandates it unconditionally. Config tweaks
and one-line bugfixes don't need that weight, but they still need a testable
contract. This feature adds an entry router that classifies each request by risk
and complexity, and a LIGHT channel (single-file `mini.md` spec) for low-risk,
low-complexity work — while keeping scenarios as the inviolable contract for
Codex on both routes.

Rollout step 2 of the flow-layer design
(`docs/plans/2026-07-03-flow-layer-design.md`); depends on handover-manager
(step 1, shipped) for context restore via `docs/handovers/LATEST.md`.

## Scope

**In scope:**
- New skill `skills/sdd-router/` — risk + complexity tiering, recommendation +
  one-line reason, user confirmation, context restore from `LATEST.md`
- Mini-spec format `docs/specs/<feature>/mini.md` (frontmatter `mode: light`,
  intent, 2–5 GIVEN/WHEN/THEN scenarios, exclusion scope)
- `hooks/prompt-submit.sh` rule text: tiered specs-before-code replaces
  unconditional FULL
- `skills/spec-driven-tdd` fingerprint: when `mini.md` exists, sha256 covers it
  alone
- `scripts/validate_specs.py` + `tests/structured-specs-integration/`
  directory-convention carve-out for mini-spec feature dirs
- verify-specs / archive-specs compatibility: mini.md scenarios verified and
  merged into `_living/` the same as delta scenarios

**Out of scope:**
- The `learn` skill (rollout step 3)
- Task time estimation / calibration (explicitly deferred in design)
- Any change to brainstormlight's ledger or spec-driven-tdd's progress.md
  semantics beyond the fingerprint file set
- A zero-spec channel — LIGHT is the minimum; no route skips scenarios

## Impact

- **Users affected:** anyone using this plugin's spec workflow — small tasks get
  a proportionate process
- **Systems affected:** prompt-submit hook, spec-driven-tdd skill,
  validate_specs.py, directory-convention tests, verify-specs and archive-specs
  skills; one new skill directory
- **Risk:** medium — the hook text change affects every turn of every session;
  a wrong carve-out in validation could let underspecified features through.
  Mitigated by: risk checks always force FULL, uncertainty escalates, tiering
  authority stays with the human, and LIGHT still requires scenarios.

## Success Criteria

- [ ] A single-file bugfix request routes LIGHT: router recommends LIGHT with a
      one-line reason, user confirms, `mini.md` is written, Codex is dispatched
      with the standard dispatch format
- [ ] Any risk hit (production, data writes/deletes, API signature, privacy)
      produces a FULL recommendation regardless of complexity
- [ ] `validate_specs.py` passes on a feature dir containing only `mini.md`
      and fails on `mini.md` with <2 or >5 scenarios or missing `mode: light`
- [ ] `pytest tests/structured-specs-integration/` green, including new
      mini-spec convention tests
- [ ] verify-specs produces a scenario→test coverage table from `mini.md`;
      archive-specs merges its scenarios into `_living/`
- [ ] Router skill passes pressure test: "urgent, just change it" still yields
      a mini.md, never zero specs
