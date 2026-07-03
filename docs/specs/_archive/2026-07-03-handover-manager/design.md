# Handover Manager Design

Source: docs/plans/2026-07-03-flow-layer-design.md (step 1 of rollout)

## Architecture

Handover is the coarse-grained cross-session/cross-tool snapshot layer.
Fine-grained in-workflow ledgers (brainstormlight grill ledger,
spec-driven-tdd progress.md, subagent-driven-development progress.md) stay
untouched; a handover references their paths instead of copying content.

Soft harness by default (skill text drives generation at wrap-up, tool switch,
phase switch) with exactly one hard-harness addition: a `PreCompact` command
hook that injects a reminder, because "context about to compact" is the moment
handovers are most needed and most forgotten. The hook cannot author the doc
(PreCompact supports command hooks only); it reminds Claude to write it.

## Components

- `skills/handover-manager/SKILL.md` — document format, triggers, iron rules,
  resume protocol. Generalizes brainstormlight's ledger pattern and adds
  git-verified file lists.
- `hooks/pre-compact.sh` — emits `hookSpecificOutput.additionalContext` with
  the reminder text; registered under `PreCompact` in `hooks/hooks.json`,
  following the existing `run-hook.cmd` polyglot dispatch pattern.
- `skills/finishing-a-development-branch/SKILL.md` — one added step: write a
  handover before presenting merge/PR options.
- `docs/handovers/` — storage convention. Timestamped docs plus `LATEST.md`
  index (a small pointer file: path + topic + status of the newest handover).

## Data Flow

1. Trigger fires (wrap-up step, tool switch, phase switch, or PreCompact
   reminder).
2. Claude runs `git diff --stat` (and `git status` for untracked files) to
   build the verified file list.
3. Claude writes `docs/handovers/YYYY-MM-DD-HHmm-<topic>.md` with the six
   required sections, then rewrites `LATEST.md` to point at it.
4. Resume: user says "continue <topic>" (any tool) → agent reads `LATEST.md`,
   opens the handover it points to, restores decisions/state, executes the
   restart instructions, and continues from open items without re-asking
   settled decisions.

## Error Handling

- Not a git repo / git unavailable: file list section states this explicitly
  instead of listing files from memory.
- No handover exists on resume: say so and fall back to normal context
  gathering; never fabricate prior state.
- `LATEST.md` points at a missing file: fall back to newest timestamped file
  in `docs/handovers/`, then repair `LATEST.md`.
- Work in progress with failing tests: verification section records the real
  failing output — embellishing progress is a spec violation, not a style
  issue.

## Dependencies

- Claude Code `PreCompact` hook event (command hooks; additionalContext
  injection) — confirmed available in hooks docs.
- Existing hook infrastructure: `hooks/hooks.json`, `hooks/run-hook.cmd`.
- `git` for diff-verified file lists.
- Future consumers (not blockers): sdd-router reads `LATEST.md`; learn chains
  off the wrap-up scan.
