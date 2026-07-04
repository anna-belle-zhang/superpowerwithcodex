---
name: learn
description: Use when capturing lessons, recurring workflow patterns, or upgrade proposals from session experience - guides confirmed lesson entry writing, tag-based dedup, promotion, and passive wrap-up scans
---

# Learn

## Overview

Capture experience as confirmed lessons, promote repeated lessons into shared patterns, and propose skill upgrades when the same tag recurs.

**Core principle:** better to miss a lesson than record a wrong one.

**Announce at start:** "I'm using the learn skill to capture lessons from this session."

## When To Use

Use this skill when:
- The user asks to note a pitfall, lesson, correction, or recurring issue.
- Handover-manager invokes the passive scan during wrap-up.
- A confirmed lesson may need dedup, pattern promotion, or an upgrade proposal.

Do not use this skill to edit another skill directly. Upgrade proposals go through `writing-skills`, including pressure testing.

## Entry Format

Write project lessons to `docs/lessons.md` and shared patterns to `~/.claude/lessons-common.md`.

```markdown
## [tag: <kebab-case-tag>] <Title>
- Symptom: ...
- Root cause: ...
- Correct approach: ...
- Occurrences: 2026-07-03 (project-a), 2026-07-04 (project-b)
- Level: lesson
```

The tag is the stable dedup key. Dedup by tag, not title text.

## Confirmation Gate

Before writing to any lessons file:
1. Draft the complete entry.
2. Shows the complete entry to the user.
3. Wait for explicit user confirmation.
4. Write only the confirmed entry.

Confidence is not confirmation. Certainty never bypasses the gate, even when the entry seems obviously correct. Until confirmation, learn writes nothing.

If the user declines a drafted entry or scan candidate, the declined item is discarded without being written or re-asked later in the session.

## Active Capture

When the user asks to note a pitfall or lesson:
1. Draft a lesson entry with a specific tag, title, symptom, root cause, correct approach, occurrence date/project, and `Level: lesson`.
2. Show the complete entry.
3. Wait for explicit user confirmation.
4. Append it to `docs/lessons.md`, or update an existing matching tag's occurrences.

If `docs/lessons.md` does not exist, learn creates the file with a header before appending the first confirmed entry.

## Passive Scan

When handover-manager's wrap-up invokes the learn scan, scan the session for:
- User corrected the approach.
- Debug loop exceeded 2 rounds.
- Technical decision was made with a stated reason.
- Same problem class recurred.

Present a candidate list for selection and write nothing until the user confirms specific entries. If there are no signals, state that no lesson candidates were found and does not invent entries to appear useful.

## Dedup And Tagging

When a confirmed lesson uses a tag that already exists in `docs/lessons.md`, the existing entry gains an occurrence line or occurrence item instead of a duplicate entry being appended.

If a symptom resembles an existing entry but has a different root cause, assign a distinct tag rather than incrementing the existing tag's occurrences.

## Promotion

On each confirmed write, count occurrences by tag.

- At 2 occurrences, offer to sync the entry to `~/.claude/lessons-common.md` with `Level: pattern`; sync only after the user confirms.
- At 3 occurrences, offer to generate an upgrade proposal document that names the target skill, the suggested constraint entry, and the supporting occurrence records.

If `~/.claude/lessons-common.md` is absent or unwritable when a pattern sync is confirmed, learn reports the failure, keeps the project-level entry intact, and does not retry silently.

Learn never edits the target skill. If the user accepts a generated upgrade proposal, learn directs the change through the normal `writing-skills` process, including pressure testing.

## Validation

Run the validator when checking lesson file format:

```bash
python scripts/validate_lessons.py docs/lessons.md
```

The validator accepts a missing lessons file because it is created lazily on first confirmed write.

## Integration

**Called by:**
- **handover-manager** after `docs/handovers/LATEST.md` is updated.
- Any session where the user asks to capture a lesson.

**Pairs with:**
- **writing-skills** for Level 3 upgrade proposals.
- **verification-before-completion** before claiming lesson files are valid.
