# Codex Plugin for Claude Code

The `codex@openai-codex` plugin integrates OpenAI Codex into Claude Code via a shared runtime. Claude plans, tests, and reviews; Codex implements.

## Installation

```bash
/plugin marketplace add openai-codex
/plugin install codex@openai-codex
```

Verify:

```bash
codex --version
codex login        # authenticate with OpenAI
/codex:setup       # confirm Claude Code can reach the runtime
```

## Commands

| Command | What it does |
|---------|-------------|
| `/codex:rescue [task]` | Delegate a task or investigation to Codex |
| `/codex:review` | Run a Codex code review against local git state |
| `/codex:adversarial-review` | Challenge-focused review (design, tradeoffs) |
| `/codex:status` | Show active and recent Codex jobs |
| `/codex:result [job-id]` | Show stored output for a finished job |
| `/codex:cancel [job-id]` | Cancel an active background job |
| `/codex:setup` | Check runtime health and toggle stop-review gate |

Common flags for `/codex:rescue`:

```
--background     Run Codex in the background, return immediately
--wait           Run in foreground (default)
--resume         Continue the most recent Codex thread
--fresh          Force a new thread even if one is resumable
--model spark    Use gpt-5.3-codex-spark
--effort high    Set reasoning effort (none/minimal/low/medium/high/xhigh)
```

## Architecture

```
/codex:rescue [args]
  └─ rescue.md fork (allowed-tools: Bash, AskUserQuestion, Agent)
       └─ Agent(codex:codex-rescue) subagent
            └─ Bash: node codex-companion.mjs task --write [prompt]
                 └─ Codex app-server (sandbox: workspace-write)
```

`codex-companion.mjs` manages job state, resume threads, background/foreground execution, and output formatting. It is the correct entry point — bypassing it (e.g. via `codex e --full-auto` directly) loses resume support and job tracking.

## Sandbox Configuration

Codex runs commands inside a sandbox. Configured in `~/.codex/config.toml`.

### Sandbox modes

| Mode | File writes | Use case |
|------|-------------|----------|
| `read-only` | No | Review, diagnosis |
| `workspace-write` | Project dir | Tasks, implementation (default for rescue) |
| `danger-full-access` | Unrestricted | Use only in externally sandboxed environments |

### Network access

Network is blocked by default. Enable it per sandbox mode:

```toml
# ~/.codex/config.toml

[sandbox_workspace_write]
network_access = true
```

This is required for tasks that run tests against external services, use package managers, or call APIs.

### Verify

```bash
codex e --full-auto "curl -s https://api.github.com/zen"
```

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| `network is unreachable` | Add `[sandbox_workspace_write] network_access = true` to `~/.codex/config.toml` |
| Config ignored | Path must be `~/.codex/config.toml` — not `~/.config/codex/` |
| Wrong TOML section | Use `[sandbox_workspace_write]` (underscores, not dots) |
| `python.exe: Permission denied` in WSL | Install native Linux `az`: `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| Azure CLI fails in sandbox | `export AZURE_CONFIG_DIR=/tmp/azure && cp -r ~/.azure /tmp/azure` |

## Skills

The superpowerwithcodex plugin provides two skills that use Codex:

**`codex-cli`** — One-off tasks (implement function, fix bug, create file). Dispatches via `codex:codex-rescue` subagent.

**`codex-subagent-driven-development`** — Full TDD workflow. Claude writes failing tests, Codex implements, Claude verifies.

## Session-Start Patches

The superpowerwithcodex `session-start.sh` hook applies two fixes to the installed codex plugin on every session start. These are idempotent and re-apply after `/plugin update codex`.

**Fix 1 — `rescue.md` missing `Agent` in `allowed-tools`:**
Without this, the rescue fork cannot use the Agent tool and falls back to `mcp__codex-subagent__spawn_agent`, which bypasses `codex-companion.mjs` entirely (no resume, no job tracking, no background mode).

**Fix 2 — `codex-rescue.md` ambiguous write rule:**
The agent definition had an exception allowing omission of `--write` for "research/diagnosis" tasks. At high effort Claude applies this exception, leaving Codex in read-only mode. The fix enforces `--write` unless the user explicitly requests read-only.

Both patches target files under `~/.claude/plugins/cache/openai-codex/codex/<version>/`.
