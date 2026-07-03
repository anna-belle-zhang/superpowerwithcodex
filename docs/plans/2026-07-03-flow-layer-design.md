# Flow Layer Design — sdd-router + handover-manager + learn

Date: 2026-07-03
Status: approved (brainstorm complete, validated section by section)
Origin: gap analysis against the zimaflow orchestration-layer concept

## Problem

Three gaps in the current workflow, identified by comparing this repo against
the zimaflow design:

1. **No entry routing.** The prompt-submit hook forces FULL spec workflow for
   every request. Config tweaks and one-line bugfixes pay the full spec cost;
   there is no risk-tiered process-weight decision.
2. **No cross-session/cross-tool handover.** brainstormlight's ledger and
   spec-driven-tdd's progress.md cover their own workflows, but there is no
   general handover doc for session end, tool switch (Claude CLI ↔ Cowork ↔
   Codex), or context-near-full moments.
3. **No experience capture.** Lessons stay in chat history and get re-learned.

Out of scope (explicitly deferred): task time estimation / calibration
dictionary — lowest value for solo+AI workflow, no historical data yet.

## Architecture

```
skills/
  sdd-router/          # entry: risk + complexity tiering → FULL / LIGHT
  handover-manager/    # exit: standardized handover docs
  learn/               # feedback: lesson → pattern → proposal
hooks/
  prompt-submit.sh     # MODIFIED: router-aware rules replace "always FULL"
  pre-compact.sh       # NEW: PreCompact reminder to write handover first
```

Core principle (from zimaflow): **orchestrate, don't rebuild.** The three
skills route, bridge, and feed back; they do not duplicate brainstorming,
writing-specs, or spec-driven-tdd. Hard harness added in exactly one place
(PreCompact reminder); everything else is skill text.

Flow: new request → sdd-router reads `docs/handovers/LATEST.md` to restore
context, classifies risk + complexity → FULL (existing brainstorm →
write-specs → spec-driven-tdd chain) or LIGHT (single-file mini-spec, still
dispatched to Codex) → on wrap-up, handover-manager writes the handover doc
and invokes learn to scan the session; all learn writes are user-confirmed.

## sdd-router

Routing rules (in skill text; condensed version injected by prompt-submit):

```yaml
risk_checks:        # any hit → FULL
  - affects real users or production systems
  - writes/deletes data, or changes an API signature
  - touches privacy, compliance, or core data
complexity:
  high: new module, multi-file, cross frontend/backend  → FULL
  low:  config change, bugfix, single file              → LIGHT
uncertain: escalate one level (doubtful LIGHT → FULL)
```

Router outputs a **recommendation + one-line reason**; the user confirms or
overrides with a word. Tiering authority always stays with the human.

**Mini-spec format** — `docs/specs/<feature>/mini.md`: YAML frontmatter with
`mode: light`, body = one-sentence intent + 2–5 GIVEN/WHEN/THEN scenarios +
exclusion scope. Skips proposal.md/design.md and brainstorming, but scenarios
remain an inviolable contract for Codex.

**Three synchronized changes** (conflicts found in research):

1. `hooks/prompt-submit.sh` — rule 1 becomes: "specs before code; weight is
   tiered by router: FULL = proposal/design/deltas, LIGHT = mini.md; any risk
   hit forces FULL."
2. `skills/spec-driven-tdd` — spec fingerprint supports mini.md (when mini.md
   exists, sha256 covers it alone).
3. `tests/structured-specs-integration/` — directory-convention tests allow a
   feature dir containing mini.md to omit proposal.md/design.md.

**verify/archive compatibility**: verify-specs runs unchanged on LIGHT
(scenario→test coverage check is identical); archive-specs merges mini-spec
scenarios into `_living/` the same as delta specs — no second-class specs.

## handover-manager

**Storage**: `docs/handovers/YYYY-MM-DD-HHmm-<topic>.md`; latest indexed at
`docs/handovers/LATEST.md` (the only file router reads for context restore).

**Format** (generalizes brainstormlight's ledger, adds git verification):

```markdown
# <topic> — Handover
Status: in-progress | blocked | done
Mode: full | light
## Decisions            (with reasons, from this session's calls)
## Changes this round   (narrative)
## File list            (MUST come from git diff --stat, never from memory)
## Verification results (test command + actual output summary; half-done = say half-done)
## Open items           (with blocked reasons)
## Restart instructions (copy-pasteable commands)
```

**Four triggers**:

| Moment | Mechanism |
|---|---|
| normal session wrap-up | skill text (extra step in finishing-a-development-branch) |
| tool switch (to Codex/Cowork) | skill text |
| context near full | **PreCompact hook** injects "write handover before compaction" |
| phase switch (spec finalized → implementation, etc.) | skill text |

**Iron rules** (in skill text): file list unverified → run `git diff`; never
embellish progress; restart instructions must be executable as-is.

**Relation to existing ledgers**: brainstormlight's grill ledger and
spec-driven-tdd's progress.md stay untouched — they are fine-grained
in-workflow state. Handover is the coarse-grained cross-session/cross-tool
snapshot; it references their paths instead of copying content.

Research note: Claude Code's PreCompact hook event exists but only supports
command hooks (can inject context / block with exit 2, cannot author docs
itself) — hence reminder-style, with Claude writing the doc before compaction.

## learn

**Storage, two levels**: project `docs/lessons.md`; shared
`~/.claude/lessons-common.md`.

**Triggers**: active ("note this pitfall") + passive (handover-manager's final
step scans the session). Scan signals: user corrected the AI's approach,
debug loop > 2 rounds, technical decision made with stated reason, same class
of problem recurring.

**Entry format** (with dedup key — research flagged that raw occurrence counts
are noisy; different root causes look like repeats):

```markdown
## [tag: codex-sandbox-network] Title
- Symptom / Root cause / Correct approach
- Occurrences: 2026-07-03 (project-a), ...
- Level: lesson | pattern
```

`tag` is the stable dedup key; promotion counts by tag:
**≥2 → sync to lessons-common.md (pattern); ≥3 → generate an upgrade proposal.**

**Level 3 proposes, never writes** (confirmed decision): the proposal is a
markdown doc naming the target skill, the suggested constraint entry, and the
supporting occurrence records. After user confirmation it goes through the
normal `writing-skills` process — including pressure testing. No bypass of
the skill-TDD iron law.

**Bottom line**: every learn write to a lessons file shows the entry and waits
for user confirmation; better to miss a lesson than record a wrong one.
Passive scans produce a candidate list, not direct writes.

## Testing strategy

1. **Skill pressure tests** (writing-skills iron law): baseline without skill,
   then with. Key scenarios — router: user says "urgent, just change it";
   handover: "session ending, in a hurry" (still runs git diff?); learn: "AI
   is confident" (still waits for confirmation?).
2. **Deterministic tests** (pytest, in `tests/structured-specs-integration/`):
   mini.md frontmatter validation; directory-convention carve-out logic;
   handover doc contains all six sections; hooks.json registers PreCompact.

## Rollout order

1. **handover-manager** — zero conflicts; pure additive skill + PreCompact hook
2. **sdd-router + LIGHT channel** — depends on handover (reads LATEST.md);
   requires the three synchronized changes (hook text, fingerprint, tests)
3. **learn** — depends on handover's wrap-up chaining; last

Each step ships independently and follows this repo's own process: write
specs → Codex implements deterministic parts → pressure-test the skill text.

## Prior art consulted

- Claude Code hooks docs (PreCompact/SessionEnd events): https://code.claude.com/docs/en/hooks
- mvara-ai/precompact-hook, Claudate/claude-code-context-sync, thedotmack/claude-mem (handover/memory prior art)
- GitHub Spec Kit constitutional gates; Kiro specs; arXiv 2602.00180 (spec rigor tiers), 2606.04967 (full vs light SDD)
- Reflexion, Voyager, MemSkill, SkillOpt (lessons-capture prior art; SkillOpt vendored at repos/SkillOpt/)
