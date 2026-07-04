---
name: handover-manager
description: Use when work is ending, switching tools, approaching compaction, or resuming from a prior handover - writes and reads coarse-grained handover snapshots for cross-session continuity
---

# Handover Manager

## Overview

Create a coarse-grained handover snapshot that another tool or session can resume from without relying on chat history.

**Core principle:** record decisions, changed files, real verification, open items, and exact restart steps.

**Announce at start:** "I'm using the handover-manager skill to preserve or restore handover context."

## When To Use

Use this skill when:
- The user says work will continue in Codex, Claude Cowork, another tool, or another session.
- The current session prepares to stop before the switch.
- Context compaction is about to run.
- A phase boundary is reached, including branch wrap-up.
- The user says "continue <topic>" and a prior handover may exist.

For tool switches, generate the handover before the switch.

## Handover Document Format

Write handover documents at:

```text
docs/handovers/YYYY-MM-DD-HHmm-<topic>.md
```

Each handover document must contain exactly these six top-level sections:

## Decisions

List decisions that were already made. Do not re-open settled decisions during resume unless the user asks.

## Changes this round

Summarize what changed in this session. Reference fine-grained ledgers by file path, such as a grill ledger or `docs/specs/<feature>/progress.md`, rather than duplicating their content.

## File list

In a git repository, derive this section from `git diff --stat` and `git status` output. Do not list files from memory. Files not confirmed by git are not listed.

If the directory is not a git repository or git is unavailable, explicitly state that git verification was unavailable instead of listing files from memory.

## Verification results

Record the actual test command and its real output summary, including failures. For failing tests or half-done tasks, report the real state without claiming more progress than occurred.

## Open items

List remaining work, blockers, and known risks. If there are none, write that there are none.

## Restart instructions

Every restart instruction must be a concrete copy-pasteable command or file path, not a vague description.

## Generation Process

1. Create `docs/handovers/` if needed.
2. Choose a short topic slug for `docs/handovers/YYYY-MM-DD-HHmm-<topic>.md`.
3. Run `git diff --stat` and `git status` before writing the file list. If git verification fails, say so in the file list section.
4. Record verification honestly, including any failing command output summary.
5. Reference workflow ledgers by path rather than copying them.
6. Write the handover document with the six required sections.
7. Rewrite `docs/handovers/LATEST.md` to point at the new document with its topic and status.
8. Invoke the learn skill's passive scan as the final wrap-up step. The learn scan runs after the handover is written, never modifies it, presents its candidate list or reports no candidates, and completes before the session is considered wrapped up.

`docs/handovers/LATEST.md` is a small index containing the newest handover path, topic, and status. Rewrite it after every new handover.

## Status Values

Use a short status in the handover and `LATEST.md`:
- `in-progress` for active work that must resume.
- `blocked` for work that cannot continue without input or an external change.
- `done` for branch wrap-up or completed work.

## Resume Protocol

When the user asks to continue a topic:

1. Read `docs/handovers/LATEST.md`.
2. Open the handover it points to.
3. Restore decisions and open items from the handover.
4. Follow the restart instructions.
5. Continue from open items; the resuming agent does not re-ask settled decisions.

If `docs/handovers/LATEST.md` points at a missing file or a file that does not exist, fall back to the newest timestamped file in `docs/handovers/`, use it, and repair `LATEST.md`.

If no handover exists, state that no handover was found and fall back to normal context gathering without fabricating prior state.

## Iron Rules

- Never list changed files from memory.
- Never claim tests passed unless the verification output shows that they passed.
- Never copy fine-grained ledger content into the handover; reference the file path.
- Never use vague restart instructions when a command or file path can be given.
- Never fabricate prior state when no handover exists.
- Never let learn scan results modify the handover document; the handover and LATEST.md remain exactly as generated.

## Integration

**Called by:**
- **finishing-a-development-branch** before merge/PR/cleanup options are presented.
- **PreCompact hook** as a reminder before compaction.
- Any session preparing for a tool switch or session boundary.

**Pairs with:**
- **spec-driven-tdd** via `docs/specs/<feature>/progress.md` references.
- **brainstorming** via grill ledger references.
- **learn** via the final passive scan during wrap-up.
