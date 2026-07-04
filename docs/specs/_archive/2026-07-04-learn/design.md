# Learn Skill Design

Source: docs/plans/2026-07-03-flow-layer-design.md (learn section, approved).

## Architecture

Three levels of experience capture, each strictly gated by user confirmation:

```
Level 1  lesson   → docs/lessons.md              (project-local)
Level 2  pattern  → ~/.claude/lessons-common.md  (shared across projects, tag count ≥2)
Level 3  proposal → docs/proposals/YYYY-MM-DD-<tag>-upgrade.md (tag count ≥3; proposes, never writes skills)
```

Core principle: **better to miss a lesson than record a wrong one.** All
writes show the entry and wait for confirmation; passive scans produce a
candidate list, never direct writes.

## Components

- `skills/learn/SKILL.md` — capture process, scan signals, promotion rules,
  confirmation gate
- `scripts/validate_lessons.py` — deterministic validation of lessons file
  format and promotion consistency (mirrors scripts/validate_specs.py)
- `skills/handover-manager/SKILL.md` — wrap-up gains a final "invoke learn
  scan" step

## Data Flow

1. **Active trigger**: user says "note this pitfall" (or equivalent) → learn
   drafts an entry → shows it → user confirms → append to docs/lessons.md
2. **Passive trigger**: handover-manager wrap-up invokes learn scan → scan the
   session for signals (user corrected the approach; debug loop > 2 rounds;
   technical decision with stated reason; same problem class recurring) →
   present candidate list → user selects → confirmed entries written
3. **Promotion**: on each confirmed write, count occurrences by tag. Count ≥2
   → offer to sync entry to lessons-common.md as `Level: pattern`. Count ≥3 →
   offer to generate an upgrade proposal document. Both offers require
   confirmation; the proposal then goes through writing-skills (with pressure
   testing) — learn never edits a skill itself.

## Entry Format

```markdown
## [tag: codex-sandbox-network] Title
- Symptom: ...
- Root cause: ...
- Correct approach: ...
- Occurrences: 2026-07-03 (project-a), 2026-07-04 (project-b)
- Level: lesson | pattern
```

`tag` is the stable dedup key — raw occurrence counts are noisy because
different root causes look like repeats; matching is by tag, not title text.

## Error Handling

- Lessons file absent → create it with a header on first confirmed write
- ~/.claude/lessons-common.md unwritable/absent → report, keep the project
  entry, skip sync
- Malformed existing entries → validator names the entry and the violated rule
- User declines a candidate → it is dropped, not queued for re-asking

## Dependencies

- handover-manager (wrap-up chaining) — already shipped
- writing-skills process — consumer of Level 3 proposals
- No hooks, no new harness surface
