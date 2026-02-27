# Context Progress: Automated Progress Tracking Across Context Compactions

**Date:** 2026-02-19
**Status:** Design Complete

## Problem

During long development sessions, Claude Code compacts context to stay within token limits. This loses:
- Current task state (what's done, what's next)
- Lessons learned (what was tried, what failed, why)
- Architecture decisions made during the session
- Key files modified and their purpose

Users currently work around this by manually asking Claude to write a progress file before compaction, then manually asking Claude to read it after. This is error-prone and easy to forget.

## Solution

A superpowers feature combining hooks (automation) and a skill (format/behavior) that:
1. Automatically saves structured progress files during work
2. Backs up raw transcripts before compaction as a safety net
3. Automatically restores context after compaction or clear
4. Provides manual save/restore commands for explicit control

## Prior Art

- [mvara-ai/precompact-hook](https://github.com/mvara-ai/precompact-hook) — PreCompact shell script sends transcript to fresh Claude API call for recovery brief
- [yuvalsuede/memory-mcp](https://github.com/yuvalsuede/memory-mcp) — Hooks on Stop/PreCompact/SessionEnd, Haiku extracts 6 memory types, two-tier storage
- [Claudate/claude-code-context-sync](https://github.com/Claudate/claude-code-context-sync) — Manual /save-session and /resume-session with structured markdown
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 6 lifecycle hooks, SQLite + vector embeddings, progressive disclosure

## Architecture

### Components

| Component | Type | Purpose |
|---|---|---|
| `skills/context-progress/SKILL.md` | Skill | Format definition, manual capture triggers, restore behavior |
| `hooks/context-progress-save.sh` | PreCompact command hook | Transcript backup safety net |
| `hooks/context-progress-restore.sh` | SessionStart command hook | Restore latest progress after compact/clear |
| TaskCompleted agent hook | In `hooks/hooks.json` | Main save — Claude writes progress file at milestones |
| `commands/save-progress.md` | Slash command | Manual checkpoint: `/superpowers:save-progress` |
| `commands/restore-progress.md` | Slash command | Manual restore: `/superpowers:restore-progress [task-slug]` |

### Folder Structure (per-project)

```
.claude/progress/
  2026-02-19T14-30-00-setup-auth-module.md
  2026-02-19T15-45-00-setup-auth-module.md
  2026-02-19T16-12-00-setup-auth-module.md
  transcripts/
    2026-02-19T16-15-00.jsonl
```

- Progress files: structured markdown with rolling summary + delta
- Transcripts: raw conversation JSONL backups (kept last 3 only)
- Added to `.gitignore` on first use

### File Naming Convention

`YYYY-MM-DDTHH-MM-SS-{task-slug}.md`

- Task slug derived from branch name or primary task subject
- Colons replaced with hyphens for filesystem safety
- Sorted chronologically by filename

## Progress File Format

```markdown
# Progress: {task description}
**Branch:** {current branch}
**Last Updated:** {ISO datetime}

## Rolling Summary
{Compact summary of ALL progress so far — key decisions,
architecture chosen, major milestones. Re-summarized from
previous file + new delta. Never just appended.}

## Current State
- [x] Completed task 1
- [x] Completed task 2
- [ ] In-progress task (in progress)
- [ ] Upcoming task

## Lessons & Failed Approaches
- Tried X because Y -> failed because Z
- Tried A because B -> failed because C
- Learned: {insight that should survive compaction}

## Key Files Modified
- path/to/file.ts — what changed and why
- path/to/other.ts — what changed and why

## Delta (since last save)
{What happened since the previous progress file was written}
```

**Size constraint:** Rolling summary re-condenses each save. Files stay under ~200 lines.

## Hook Design

### 1. PreCompact Hook — Transcript Backup

**File:** `hooks/context-progress-save.sh`
**Trigger:** `auto|manual` (both compaction types)
**Type:** command (PreCompact only supports command hooks)

Behavior:
1. Read hook input from stdin (JSON with `transcript_path`)
2. Parse `transcript_path` using lightweight JSON extraction
3. If transcript file exists, copy to `.claude/progress/transcripts/{datetime}.jsonl`
4. Prune to keep only last 3 transcript backups
5. Exit 0 (non-blocking)

Note: PreCompact cannot block compaction, cannot use prompt/agent hooks, and cannot inject context. This hook is purely a safety net backup.

### 2. TaskCompleted Hook — Main Progress Save

**Configured in:** `hooks/hooks.json`
**Type:** agent (has tool access — can Read/Write files)
**Timeout:** 120 seconds

Prompt:
```
A task was just completed. Update the context progress file
following the context-progress skill. Read the latest .md file
in .claude/progress/ (if any), condense its rolling summary,
add the new delta, and write a new progress file. Include
current task state, any lessons learned or failed approaches,
and key files modified. $ARGUMENTS
```

The agent hook spawns a fresh Claude instance with tool access that:
1. Reads the latest progress file (if exists)
2. Condenses the rolling summary
3. Writes a new file with updated state

### 3. SessionStart Hook — Restore After Compaction

**File:** `hooks/context-progress-restore.sh`
**Trigger:** `compact|clear` only (not startup/resume — those have full context)
**Type:** command

Behavior:
1. Find project root (walk up from cwd looking for `.git/` or `.claude/`)
2. Look for `.claude/progress/*.md` files
3. Sort by filename, take the latest
4. If found: return JSON with `additionalContext` containing:
   ```
   <context-progress>
   You were working on this before context compaction.
   Read it carefully and continue where you left off.

   {file contents}
   </context-progress>
   ```
5. If no files: return empty `additionalContext` (no-op)

## Commands

### `/superpowers:save-progress`

**File:** `commands/save-progress.md`
**Purpose:** Manual checkpoint — save progress immediately without waiting for TaskCompleted

Use cases:
- About to do something risky
- Breakthrough insight worth capturing now
- Anticipating manual `/compact`
- Switching focus to a different task

Implementation: Command triggers the skill, Claude writes a progress file immediately.

### `/superpowers:restore-progress`

**File:** `commands/restore-progress.md`
**Purpose:** Manual restore — load progress from a previous session or specific task

Behavior:
- No args: load the latest progress file
- With task slug: fuzzy match on slug (e.g., `/superpowers:restore-progress auth`)
- Multiple matches: present list and ask user which one
- No matches: inform user no progress files found

Use cases:
- Fresh session (not compact/clear) picking up previous work
- Loading a specific task's progress when multiple exist
- Parallel sessions working on different tasks

## Skill Design

### `skills/context-progress/SKILL.md`

**Frontmatter:**
```yaml
name: context-progress
description: Use when working on multi-step tasks that span
  context compactions - maintains rolling progress files with
  task state, lessons learned, and failed approaches in
  .claude/progress/ so context is preserved automatically
```

**Skill instructs Claude to:**

1. **On session start with injected progress context** — read it carefully, orient, and continue where the previous context left off

2. **During work** — hooks handle automatic saves at TaskCompleted, but also capture progress when:
   - A significant lesson is learned
   - An approach is tried and fails (record what, why, and the failure reason)
   - Architecture decisions are made
   - Switching between subtasks

3. **File naming** — derive task-slug from branch name or primary task subject

4. **Rolling summary rule** — each new file re-condenses previous summary + new delta. Never just append. Keep under ~200 lines

5. **Cleanup on completion** — when task is fully done (branch merged), delete progress files or move to `.claude/progress/archive/`

6. **Gitignore** — add `.claude/progress/` to `.gitignore` on first use if not already present

**What the skill does NOT do:**
- No automatic saves (hooks handle that)
- No restore injection (SessionStart hook handles that)
- Defines format and behavior only

## Integration with Existing Skills

| Skill | Interaction |
|---|---|
| `executing-plans` / `subagent-driven-development` | TaskCompleted fires after each task — auto-saves |
| `brainstorming` | Design decisions captured as lessons in progress file |
| `finishing-a-development-branch` | Triggers cleanup of progress files |
| `using-git-worktrees` | Each worktree has its own `.claude/progress/` — parallel isolation |
| `verification-before-completion` | Verification results captured in progress |

## Implementation Plan

### Task 1: Create the skill
- Write `skills/context-progress/SKILL.md` with frontmatter and full instructions
- Defines format, behavior, cleanup rules

### Task 2: Create PreCompact hook
- Write `hooks/context-progress-save.sh`
- Reads transcript_path from stdin JSON, copies to `.claude/progress/transcripts/`
- Prunes to last 3 backups

### Task 3: Create SessionStart restore hook
- Write `hooks/context-progress-restore.sh`
- Finds latest progress file, returns as additionalContext JSON
- Only fires on compact|clear

### Task 4: Update hooks.json
- Add PreCompact entry for context-progress-save.sh
- Add SessionStart entry for context-progress-restore.sh (compact|clear matcher)
- Add TaskCompleted agent hook with progress-save prompt

### Task 5: Create commands
- Write `commands/save-progress.md`
- Write `commands/restore-progress.md`

### Task 6: Update CLAUDE.md
- Add context-progress to commands list
- Add `.claude/progress/` to directory structure

### Task 7: Test
- Verify PreCompact hook copies transcript
- Verify TaskCompleted hook writes progress file
- Verify SessionStart hook restores progress
- Verify `/save-progress` and `/restore-progress` commands work
- Test with parallel worktrees
