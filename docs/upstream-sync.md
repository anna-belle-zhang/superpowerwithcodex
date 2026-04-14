# Upstream Sync Tracker — obra/superpowers

**Upstream:** https://github.com/obra/superpowers  
**Fork point (merge-base):** `76cb215`  
**Analysis date:** 2026-04-15  
**Commits behind upstream:** 431

---

## Status Key

| Symbol | Meaning |
|---|---|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Done |
| ❌ | Skipped / ignored |

---

## Group 1 — Cherry-pick (safe, no conflicts)

These are additive, do not overlap with our Codex additions, and can be applied cleanly.

| Status | SHA | Subject |
|---|---|---|
| ⬜ | `eccd453` | Add Contributor Covenant Code of Conduct |
| ⬜ | `7642153` | Add PR template |
| ⬜ | `8ea3981` | Add issue templates and disable blank issues |
| ⬜ | `c0b417e` | Add contributor guidelines to reduce agentic slop PRs |
| ⬜ | `dd23728` | Add agent-facing guardrails to contributor guidelines |
| ⬜ | `74a0c00` | docs: add Codex App compatibility design spec (PRI-823) |
| ⬜ | `2b1bfe5` | docs(codex-tools): add named agent dispatch mapping for Codex |
| ⬜ | `2d942f3` | fix(opencode): align skills path across bootstrap, runtime, and tests |

**Command to apply:**
```bash
git cherry-pick eccd453 7642153 8ea3981 c0b417e dd23728 74a0c00 2b1bfe5 2d942f3
```

---

## Group 2 — Manual merge required

These have real content divergence with our fork. Each needs a read-and-reconcile pass.

### 2a. Brainstorming skill chain (highest priority)

Our change: added discovery subagent step after understanding purpose.  
Upstream changes: hard gates, visual companion, scope assessment, spec review loop, plan review loop.

| Status | SHA | Subject | Our concern |
|---|---|---|---|
| ⬜ | `7f2ee61` | Enforce brainstorming workflow with hard gates and process flow | Merge hard gates into our version |
| ⬜ | `866f2bd` | Add visual companion integration to brainstorming skill | Evaluate — may conflict with discovery step |
| ⬜ | `d48b14e` | Add project-level scope assessment to brainstorming pipeline | Additive, likely compatible |
| ⬜ | `ec3f7f1` | fix(brainstorming): add user review gate between spec and writing-plans | Good improvement, absorb |
| ⬜ | `9d2b886` | Fix brainstorming skill: add spec review loop to checklist | Good improvement, absorb |

**File:** `skills/brainstorming/SKILL.md`  
**Approach:** Read upstream diff, manually integrate improvements that don't displace our discovery subagent step.

### 2b. Writing plans

| Status | SHA | Subject | Our concern |
|---|---|---|---|
| ⬜ | `7b99c39` | Add plan review loop and checkbox syntax to writing-plans skill | Worth absorbing, no direct conflict |

**File:** `skills/writing-plans/SKILL.md`

### 2c. Delegation and review policy

| Status | SHA | Subject | Our concern |
|---|---|---|---|
| ⬜ | `9ccce3b` | Add context isolation principle to all delegation skills | Apply to our codex-executor and gemini-executor agents |
| ⬜ | `e6221a4` | Replace subagent review loops with lightweight inline self-review | Evaluate against our Codex executor pattern |
| ⬜ | `3f80f1c` | Reapply: Replace subagent review loops with lightweight inline self-review | Same as above (reapply commit) |

**Files:** `skills/subagent-driven-development/SKILL.md`, `agents/codex-executor.md`

### 2d. Commands / slash command deprecation

| Status | SHA | Subject | Our concern |
|---|---|---|---|
| ⬜ | `c3ecc1b` | Deprecate slash commands in favor of skills | Decide: keep or kill our slash commands |

**Files:** `commands/brainstorm.md`, `commands/execute-plan.md`, `commands/write-plan.md`  
**Decision needed:** Our fork uses commands as first-class entry points tied to structured-spec flow. Upstream is moving to skills-only.

### 2e. using-superpowers references

| Status | SHA | Subject | Our concern |
|---|---|---|---|
| ⬜ | (part of `21a774e`) | Load Gemini tool mapping, update using-superpowers references | Our using-superpowers diverged — check for additive references |

**File:** `skills/using-superpowers/SKILL.md`

---

## Group 3 — Ignore

Architecturally incompatible with our fork's design choices.

| SHA range | Subject | Reason |
|---|---|---|
| `bdd45c7`–`715e18e` | Gemini CLI extension chain (5 commits) | Upstream uses `gemini-extension.json`; we use `skills/gemini-cli/SKILL.md` + `agents/gemini-executor.md`. Different architecture, incompatible. |
| `8c8c5e8`–`777a977` | sync-to-codex-plugin mirroring chain (6 commits) | Upstream's plugin-sync automation conflicts with our plugin identity (anna-belle-zhang/superpowerwithcodex). |
| `8b16692` | Add Copilot CLI tool mapping | We don't use Copilot; skip unless needed. |

---

## Upstream test infrastructure

Upstream added non-overlapping test suites in `tests/`. These are safe to take but need review to ensure they don't assume upstream-only skill content.

| Status | Directory | Notes |
|---|---|---|
| ⬜ | `tests/brainstorm-server/` | Check for brainstorming skill assumptions |
| ⬜ | `tests/claude-code/` | Likely safe |
| ⬜ | `tests/explicit-skill-requests/` | Likely safe |
| ⬜ | `tests/skill-triggering/` | Likely safe |
| ⬜ | `tests/subagent-driven-dev/` | Check against our executor changes |

---

## Notes

- Do not attempt a full `git merge upstream/main` — 431 commits with 11 direct-conflict files makes it impractical.
- Preferred flow: cherry-pick Group 1 → manual merge Group 2 in priority order → ignore Group 3.
- After each Group 2 manual merge, run tests before proceeding to the next.
- Update this doc as items are completed.
