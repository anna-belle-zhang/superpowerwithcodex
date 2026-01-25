# Ralph-Codex-E2E Hybrid Workflow Design

**Date:** 2026-01-25
**Status:** Design Complete - Ready for Implementation
**Goal:** Integrate Ralph Wiggum loop with Codex (dev + unit + integration tests) and Claude Code (E2E tests)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RALPH WIGGUM LOOP                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌──────────┐  │  │
│  │  │   CODEX     │───▶│   CODEX     │───▶│  CLAUDE  │  │  │
│  │  │ Dev + Unit  │    │ Integration │    │   E2E    │  │  │
│  │  │   Tests     │    │   Tests     │    │  (auto)  │  │  │
│  │  └─────────────┘    └─────────────┘    └──────────┘  │  │
│  │                                              │        │  │
│  │                                     ┌────────┴───────┐│  │
│  │                                     │ Project Type?  ││  │
│  │                                     ├────────────────┤│  │
│  │                                     │ Web → Playwright│  │
│  │                                     │ API → Bash/curl ││  │
│  │                                     │ CLI → Bash      ││  │
│  │                                     └────────────────┘│  │
│  │                                                       │  │
│  │              All Tests Green? ──▶ EXIT LOOP           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Role |
|-----------|------|
| **Ralph Wiggum** | Outer loop via Stop hook, re-injects prompt until all tests pass |
| **Codex** | Implementation + unit tests + integration tests (network enabled) |
| **Claude Code** | E2E tests only (project-specific detection) |

### E2E Detection Logic

- Has `playwright.config.*` or `cypress.config.*` → Browser E2E
- Has `package.json` with web framework → Browser E2E
- Has OpenAPI/Swagger spec → API E2E
- Default → Bash-based system tests

---

## 2. Prerequisites & Setup

### Step 1: Codex Network Configuration

Create/edit `~/.config/codex/config.toml`:

```toml
[sandbox.workspace_write]
network_access = true
```

This enables network for all Codex operations (required for integration tests hitting APIs, databases, Azure CLI).

### Step 2: Install Ralph Wiggum Plugin

```bash
/plugin install ralph-wiggum@claude-plugins-official
```

### Step 3: Verify MCP Configuration

Ensure `.mcp.json` contains:

```json
{
  "mcpServers": {
    "codex-subagent": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}
```

### Step 4: Install Skill

New skill at `skills/ralph-codex-e2e/SKILL.md` replaces `execute-plan` when Ralph mode is chosen.

---

## 3. Execution Flow

### Ralph Loop Prompt Structure

```bash
/ralph-loop "Execute plan: docs/plans/YYYY-MM-DD-feature-design.md

For each task:
1. CODEX: Implement feature + write unit tests + write integration tests
2. Run unit tests → must pass
3. Run integration tests → must pass
4. CLAUDE: Run E2E tests (auto-detect project type)
5. E2E must pass

Loop until ALL tests green for ALL tasks.
" --max-iterations 30
```

### Per-Task Cycle

```
┌─────────────────────────────────────────────────────────┐
│ TASK N                                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. CODEX PHASE                                         │
│     ├─ Read task from plan                              │
│     ├─ Implement code                                   │
│     ├─ Write unit tests                                 │
│     ├─ Write integration tests                          │
│     ├─ Run unit tests                                   │
│     │   └─ Fail? → Codex retry (2x) → Claude fix (2x)  │
│     └─ Run integration tests                            │
│         └─ Fail? → Codex retry (2x) → Claude fix (2x)  │
│                                                         │
│  2. CLAUDE PHASE                                        │
│     ├─ Detect project type                              │
│     ├─ Run E2E tests (Playwright/Bash/curl)            │
│     │   └─ Fail? → Claude retry (2x) → loop back       │
│     └─ Commit if all green                              │
│                                                         │
│  3. CHECK                                               │
│     └─ All green? → Next task                           │
│        Any fail? → Ralph loops with same prompt         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Retry Chain

| Stage | Agent | Max Retries | On Exhaust |
|-------|-------|-------------|------------|
| Unit test fail | Codex | 2 | Claude fix (2x) |
| Integration test fail | Codex | 2 | Claude fix (2x) |
| E2E test fail | Claude | 2 | Ralph loops |
| All retries exhausted | - | - | Human escalation |

---

## 4. Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `skills/ralph-codex-e2e/SKILL.md` | Main skill definition |
| `lib/ralph-orchestrator.js` | Orchestration logic for Codex → Claude handoff |

### Modified Files

| File | Changes |
|------|---------|
| `docs/codexintetest.md` | Rewrite with global config instructions |
| `skills/writing-plans/SKILL.md` | Add execution strategy choice: Ralph vs standard |
| `lib/codex-integration.js` | Add E2E detection + Claude handoff functions |

---

## 5. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Test ownership | Codex: unit + integ, Claude: E2E | Codex faster for implementation loop, Claude better for system validation |
| Network strategy | Global config | Simplest setup, one-time configuration |
| Orchestration | Sequential handoff | Clear separation, predictable flow |
| Completion criteria | All tests green | Verifiable, no ambiguous promises |
| Retry strategy | Same-agent first | Exhaust agent capability before escalating |
| E2E detection | Project-specific auto | Flexible across project types |
| Integration point | Ralph replaces execute-plan | Clean substitution in superpowers cycle |

---

## 6. Success Criteria

- ✅ Codex can run integration tests (network enabled)
- ✅ Ralph loops until all test types pass
- ✅ Seamless handoff between Codex and Claude
- ✅ Auto-detects E2E strategy per project
- ✅ Retries exhaust before human escalation
- ✅ Works with existing superpowers brainstorm → write-plan workflow

---

## 7. Implementation Roadmap

### Phase 1: Infrastructure
1. Update `docs/codexintetest.md` with network fix
2. Extend `lib/codex-integration.js` with E2E detection
3. Create `lib/ralph-orchestrator.js`

### Phase 2: Skill Development
1. Create `skills/ralph-codex-e2e/SKILL.md`
2. Add retry chain logic for cross-agent handoff
3. Implement project type detection

### Phase 3: Integration
1. Modify `writing-plans` to offer Ralph execution choice
2. Test with real project
3. Document troubleshooting

---

**Design Status:** ✅ Complete and Validated
**Next Step:** Create implementation plan using `writing-plans` skill
