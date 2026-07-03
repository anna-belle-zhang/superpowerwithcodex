# Handover Manager Proposal

## Intent

Context breaks every time work moves across a session boundary — session end,
tool switch (Claude CLI ↔ Claude Cowork ↔ Codex), context compaction, or a
phase switch. Existing ledgers (brainstormlight grill ledger, spec-driven-tdd
progress.md) are workflow-internal and fine-grained; nothing produces a
standardized, coarse-grained handover snapshot that any tool can resume from.
The most common failure is simply forgetting to write one at the moment it
matters most (context about to compact, user in a hurry to leave).

## Scope

**In scope:**
- New skill `skills/handover-manager/SKILL.md` defining the handover document
  format, triggers, iron rules, and resume protocol
- Handover docs stored at `docs/handovers/YYYY-MM-DD-HHmm-<topic>.md` with a
  `docs/handovers/LATEST.md` index pointing at the newest one
- New `PreCompact` hook (`hooks/pre-compact.sh` + `hooks/hooks.json` entry)
  that injects a reminder to write the handover before compaction
- One added step in `skills/finishing-a-development-branch/SKILL.md` to write
  a handover at branch wrap-up
- Deterministic pytest checks in `tests/structured-specs-integration/`

**Out of scope:**
- sdd-router (step 2 of the flow-layer design; consumes LATEST.md later)
- learn (step 3; chains off handover wrap-up later)
- Automatic handover authoring from the hook itself (PreCompact only supports
  command hooks that inject context — Claude writes the doc, not the hook)
- Cross-project registry; handover is per-repo, keyed by CWD

## Impact

- **Users affected:** plugin users switching tools or ending sessions mid-work
- **Systems affected:** `skills/` (one new, one modified), `hooks/hooks.json`,
  new `hooks/pre-compact.sh`, `docs/handovers/` convention, integration tests
- **Risk:** low — purely additive skill + one reminder hook; no change to the
  spec workflow, dispatch format, or existing ledgers

## Success Criteria

- [ ] Handover skill produces docs containing all six required sections
- [ ] File list in a handover is generated from `git diff`, never from memory
- [ ] `LATEST.md` always points at the most recent handover after generation
- [ ] PreCompact hook is registered and injects the write-handover reminder
- [ ] finishing-a-development-branch includes the handover step
- [ ] Saying "continue <topic>" in a fresh session restores context from the
      latest handover without re-asking settled decisions
- [ ] `pytest tests/structured-specs-integration/` passes with new checks
