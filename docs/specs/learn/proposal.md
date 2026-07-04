# Learn Skill Proposal

## Intent

Lessons currently stay in chat history and get re-learned every session. The
learn skill captures experience as structured lesson entries, promotes
recurring lessons to shared patterns, and — at three occurrences — generates
an upgrade proposal for the relevant skill. It is the feedback leg of the flow
layer (sdd-router = entry, handover-manager = exit, learn = feedback).

## Scope

**In scope:**
- New skill `skills/learn/SKILL.md` — active capture ("note this pitfall") and
  passive session scan (invoked by handover-manager's wrap-up)
- Two-level storage: project `docs/lessons.md`, shared `~/.claude/lessons-common.md`
- Tag-based dedup and promotion: ≥2 occurrences → pattern (sync to
  lessons-common.md), ≥3 → upgrade proposal document
- Validator `scripts/validate_lessons.py` for lesson entry format and
  promotion-count consistency
- Convention tests in `tests/structured-specs-integration/`
- One-line addition to handover-manager's wrap-up chaining

## Out of scope
- Automatic (unconfirmed) writes to any lessons file — every write is
  user-confirmed
- Direct skill edits from Level 3 — proposals go through the normal
  writing-skills process including pressure testing
- Task time estimation / calibration dictionary (deferred in flow-layer design)

## Impact
- **Users affected:** anyone using the superpowerwithcodex workflow
- **Systems affected:** new skill + validator; handover-manager skill text
  gains one chaining step; no hook changes
- **Risk:** low — additive skill text plus a standalone validator; the only
  modified component is one wrap-up step in handover-manager

## Success Criteria
- [ ] Every learn-delta scenario has a corresponding test or pressure-test
- [ ] validate_lessons.py passes on well-formed lessons files and rejects each
      malformed case with a named error
- [ ] Pressure test: "AI is confident" scenario still waits for user
      confirmation before writing
- [ ] handover-manager wrap-up invokes the learn scan and existing
      handover-manager behaviors are unchanged
