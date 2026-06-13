# Specs-Driven Development Review — Findings Analysis

**Date:** 2026-06-13
**Scope reviewed:** `E:\A\OpenMetadata\docs\specs` (9 archived features, 26 living specs, produced by the `superpowerwithcodex` plugin workflow: brainstorm → write-specs → spec-driven-tdd via Codex → verify-specs → archive-specs)
**Related:** `E:\A\superpowerwithcodex\clauderegression.md` (March–April 2026 Claude instruction-adherence regression and its April 23 post-mortem)
**Fix plans:**
- Plugin: `E:\A\superpowerwithcodex\docs\plans\2026-06-13-specs-workflow-skill-gaps-fix.md`
- OpenMetadata: `E:\A\OpenMetadata\docs\plans\2026-06-13-specs-hardening-and-upstream-alignment.md` (renamed from `2026-06-13-specs-process-cleanup.md`; expanded with upstream-alignment tasks and March retrospective)

---

## Verdict

The parts of the workflow the plugin skills script are executed with high fidelity — delta→living merge accuracy, provenance tagging, 1:1 scenario-to-test traceability, live verification evidence in progress.md. Every gap found falls into one of two causes, separable by date:

1. **Model regression residue** (March 4 – April 20, 2026): instructions existed in skills but were not followed. The acute cause is fixed (Claude Code ≥ v2.1.116); only one-time cleanup remains.
2. **Skill design gaps** (persist with a healthy model): instructions never existed, proven by post-fix features (April 25/29) that were executed flawlessly yet still exhibit the gaps.

**Attribution test used:** instruction existed but wasn't followed → *model regression*; instruction never existed → *skill gap*.

**Regression window (per Anthropic's April 23 post-mortem):**
- March 4: default reasoning effort silently dropped high→medium (reverted April 7)
- March 26 – April 10: caching bug cleared thinking/session state every turn
- April 16 – 20: anti-verbosity system-prompt change hurt coding quality
- Acute community-reported phase: ~March 16 onward

---

## Findings Table

| # | Finding | Evidence | When introduced | Root cause | Attribution rationale | Severity | Fix |
|---|---------|----------|----------------|------------|----------------------|----------|-----|
| 1 | `_living/ARCHITECTURE.md` index ~6 weeks stale — 11 of 26 living specs unindexed; header still says "as of 2026-03-08" | `databricks-ai-*` (5), `unitycatalog-routines`, clause-role suite (4), `audit-live-clients` all missing from index | Apr 14 – Apr 29 archives, incl. **post-fix** runs | **Skill gap** | `ARCHITECTURE.md` appears nowhere in any plugin skill; healthy model executed `archiving-specs` faithfully on Apr 25/29 and still didn't touch it | High | Plugin plan Task 5; OM plan Task 1 |
| 2 | No `technical-debt.md` ever produced across 9 features; real debt buried in `progress.md` Issues sections | e.g. "runtime weighting covered with unit-level provider injection" recorded in `2026-04-29-uc-clause-role-clustering/progress.md` instead of a debt file | Structural (all features) | **Skill gap** ×3 | (a) no upstream skill instructs Codex to write `DEBT:` annotations; (b) `verifying-specs` scan hardcodes C-style `// DEBT:` — never matches Python `# DEBT:`; (c) REMOVED-delta debt source never fires on greenfield all-ADDED features | High | Plugin plan Tasks 2–4; OM plan Task 2 |
| 3 | `2026-03-11-superfund-report-v2` archive missing `progress.md` | Only feature of 9 without one | ~Mar 11, archived Mar 12 | **Model regression** | `spec-driven-tdd` mandates progress.md — instruction existed, wasn't followed; inside window | Medium | OM plan Task 3; prevention: plugin plan Task 6 |
| 4 | Mangled progress.md required repair | OpenMetadata commit `effa9b9b14` (Apr 1): "restore original progress.md structure" | Apr 1 | **Model regression** | Inside Mar 26–Apr 10 caching-bug window (session state cleared every turn) | Medium (already repaired) | None — historical corroboration |
| 5 | Archive junk: `progress copy.md`; loose `*-superseded.md` files at `_archive` root | `2026-03-03-3d-lineage-ingestion/progress copy.md`; `_archive/2026-03-08-{ado-dump,audit-log,az-dump}-superseded.md` | Mar 8–12 archiving runs | **Model regression** | Sloppy mechanical execution during acute window | Low | OM plan Task 3 |
| 6 | Loose spec at feature root instead of `specs/` | `2026-04-25-databricks-ai-governance/2026-04-25-databricks-ai-explore-ui.md` | Apr 25 (**post-fix**) | **Skill gap** | `archiving-specs` Step 3 is a blind `mv` — strays ride along by design | Low | Plugin plan Task 6; OM plan Task 3 |
| 7 | `verifying-specs` Step 4e contains duplicated contradictory "If no:" branches | `skills/verifying-specs/SKILL.md:182-183` | Skill edit Mar 12 | **Model regression** (authoring-time) | The debt section (Steps 4a–4e) was *written* during the window — editing artifact in the process doc. Confirmed same origin as the `// DEBT:` hardcoding (finding 2b): both entered in commit `91da369` (2026-03-12), the only edit to this skill since its 2026-02-19 creation | Medium | Plugin plan Tasks 1, 7 |
| 8 | Heavy trial-and-error debugging artifacts in archives | `debugging-journey.md` (Apr 14), `debug-notes.md`, `retrospective.md` (Apr 21) | Apr 14–21 (window tail) | **Model regression** | Matches reported "trial-and-error instead of structured analysis"; silver lining: artifacts preserved | Info | None — useful history |
| 9 | ~2 months of spec state uncommitted in OpenMetadata | 4 archive dirs + 6 living specs untracked; half-staged `databricks-dbt-ingestion` delete | Apr 12 onward | **Process** (repo's "no git unless asked" rule) | `archiving-specs` Step 4 commits, but runs were left unstaged | Medium (data-loss risk) | User decision; noted in OM plan |
| 10 | Formatting nit: missing blank line after first provenance tag | `_living/clause-role-extraction.md:10-11` | Apr 29 | Trivial | — | Trivial | OM plan Task 4 |

---

## Summary by Root Cause

| Root cause | Findings | Status |
|---|---|---|
| Model regression (Mar 4 – Apr 20, fixed in Claude Code ≥ v2.1.116) | #3, #4, #5, #7, #8 | Acute cause **resolved**; residue needs one-time cleanup |
| Skill design gaps (persist with healthy model) | #1, #2, #6 | **Open** — only these fixes prevent recurrence |
| Process / trivial | #9, #10 | Housekeeping |

## What Worked Throughout (keep doing)

- **Delta→living merge fidelity:** all ADDED scenarios correctly appended with `*Added: YYYY-MM-DD via <feature>*` provenance tags, including scenarios added mid-flight.
- **Test traceability:** scenario titles map 1:1 to test names (e.g. "Parser Falls Back To Dialect-Agnostic Mode On Databricks Failure" → `test_parser_falls_back_to_dialect_agnostic_mode_on_databricks_failure`).
- **Verification evidence in progress.md:** live OM UI values recorded, known gaps stated honestly.
- **Archive completeness of narrative artifacts:** retrospectives and debugging journeys preserved.
- **`UserPromptSubmit` rules-reinjection hook:** the durable mitigation from the regression episode ("hooks are guarantees, skills are guidance") is implemented and firing every turn.

## Durable Lesson

The regression episode validated the fork's architecture: critical rules enforced via hooks survive model-quality dips; skill prose does not. The remaining work is purely skill-content fixes (plugin plan) and one-time repo cleanup (OpenMetadata plan). Additionally, the debt-tracking section of `verifying-specs` was authored on 2026-03-12 (commit `91da369`) — inside the regression window — so it warrants a full proofread, not just spot fixes. (`archiving-specs` was authored 2026-02-19, *before* the window, and never edited since; its blind-`mv` gap in finding 6 is an ordinary design gap, not a window artifact. Proofreading it is still cheap and worthwhile, but on its own merits.)
