# claudecode-companion.mjs Design

**Date:** 2026-04-15  
**Goal:** Symmetric counterpart to `codex-companion.mjs` — lets Codex call Claude Code (CC) headlessly, mirroring the existing CC→Codex pattern.

## Context

`codex-companion.mjs` (CC→Codex) lives at:
```
repos/codex-plugin-cc/plugins/codex/scripts/codex-companion.mjs
```

`claudecode-companion.mjs` (Codex→CC) lives alongside it:
```
repos/codex-plugin-cc/plugins/codex/scripts/claudecode-companion.mjs
```

## Scope: v1

Single subcommand: `task`. Foreground only (no background/detach). No job tracking system.

## CLI Surface

```
node scripts/claudecode-companion.mjs task [prompt]
  --write              allow CC to edit/write files (default: read-only)
  --model <model>      override model (default: claude-sonnet-4-6)
  --max-turns <n>      cap turns (default: 10)
  --json               emit JSON envelope instead of rendered text
  --prompt-file <path> read prompt from file
  --cwd <path>         working directory (default: process.cwd())

node scripts/claudecode-companion.mjs --help
```

Prompt may also come from piped stdin (via `readStdinIfPiped` from `lib/fs.mjs`).

## Reused Utilities

| Import | Purpose |
|--------|---------|
| `lib/args.mjs` → `parseArgs`, `splitRawArgumentString` | CLI arg parsing |
| `lib/process.mjs` → `binaryAvailable` | Auth/binary preflight |
| `lib/fs.mjs` → `readStdinIfPiped`, `ensureAbsolutePath` | Prompt reading |

## Auth Preflight

Before spawning, check CC is available and authenticated:

```js
const status = binaryAvailable('claude', ['--version'], { cwd });
if (!status.available) {
  throw new Error(
    'Claude Code CLI not found. Install it and ensure `claude` is on PATH.'
  );
}
```

`binaryAvailable` already handles Windows (`shell: true` via `spawnSync`).

## Claude Invocation

```js
const claudeBin = process.platform === 'win32' ? 'claude.cmd' : 'claude';

const args = [
  '-p', prompt,
  '--output-format', 'stream-json',  // JSONL streaming, not single envelope
  '--verbose',                        // REQUIRED: stream-json in -p mode needs --verbose
  '--max-turns', String(maxTurns),
  '--model', model,
];

if (!write) {
  // Read-only: inspection tools only
  args.push('--allowedTools', 'Read,Glob,Grep,WebFetch,WebSearch');
} else {
  // Write-enabled: full file manipulation
  args.push('--allowedTools', 'Read,Glob,Grep,Edit,Write,Bash,WebFetch,WebSearch');
}

const child = spawn(claudeBin, args, {
  cwd,
  env: { ...process.env, CLAUDE_COMPANION_DEPTH: '1' },
  shell: process.platform === 'win32',
});
```

> **Note:** `--bare` is not a valid CC flag (silently ignored). To skip hook loading,
> use `--no-session-persistence` in future versions if/when CC supports it.

## Recursion Guard

Set `CLAUDE_COMPANION_DEPTH=1` in the child's env. At entry, check:

```js
if (process.env.CLAUDE_COMPANION_DEPTH) {
  throw new Error('Recursive claudecode-companion call detected. Aborting.');
}
```

This prevents CC from calling back into this companion in a loop.

## Output Handling

`stream-json` emits JSONL — one JSON object per line. Verified event shapes (CC v2.1.109):

```jsonc
// system:init — emitted first, contains model name
{ "type": "system", "subtype": "init", "model": "claude-sonnet-4-6", ... }

// assistant — text is nested inside message.content[], NOT a top-level "text" field
{ "type": "assistant", "message": { "content": [{ "type": "text", "text": "..." }], ... } }

// result — final output; cost is "total_cost_usd", model under "modelUsage" keys
{ "type": "result", "result": "...", "total_cost_usd": 0.001,
  "modelUsage": { "claude-sonnet-4-6": { ... } } }
```

**Parsing assistant text:**
```js
const content = event.message?.content ?? [];
const text = content.filter(c => c.type === 'text').map(c => c.text).join('');
```

**Parsing result:**
```js
finalResult = event.result;
costUsd = event.total_cost_usd;              // NOT event.cost_usd
resultModel = Object.keys(event.modelUsage ?? {})[0];  // NOT event.model
```

**Non-`--json` mode:** stream `assistant` text as it arrives; fall back to `result.result` if no assistant text received.

**`--json` mode:** buffer everything, emit one envelope at close:
```json
{ "status": 0, "result": "...", "model": "claude-sonnet-4-6", "costUsd": 0.001 }
```

**stderr:** always relay `child.stderr` directly to `process.stderr`.

> **Ignored event types:** `system:hook_started`, `system:hook_response`, `rate_limit_event`
> — these are emitted by `--verbose` mode but carry no output needed by the caller.

## Error Handling

| Failure | Behaviour |
|---------|-----------|
| Binary not found | `binaryAvailable` preflight throws before spawn |
| Spawn error (`child.on('error')`) | Write to stderr, `process.exitCode = 1` |
| Non-zero exit | Propagate: `child.on('close', code => process.exitCode = code ?? 1)` |
| No prompt provided | Throw with usage hint before spawning |
| Recursion detected | Throw at entry before any work |

## Security Model

- Read-only by default — safe for analysis tasks (CC reads files, returns text)
- `--write` is explicit opt-in — Codex caller must consciously request file mutation
- `--allowedTools` is the only tool-surface control — `--bare` is not a valid CC flag
- `--max-turns` caps runaway sessions
- No `--dangerously-skip-permissions` / bypassPermissions — use `--allowedTools` instead

## Data Flow

```
Codex session
  │
  └─ node claudecode-companion.mjs task "Review this implementation"
       │
       ├─ preflight: binaryAvailable('claude')
       ├─ recursion guard: check CLAUDE_COMPANION_DEPTH
       ├─ spawn: claude -p "..." --output-format stream-json --verbose ...
       │    │
       │    ├─ stream-json JSONL events → stdout
       │    └─ errors → stderr
       │
       └─ relay output to Codex, propagate exit code
```

## What's Explicitly Out of Scope (v1)

- Background/detach mode (no job tracking)
- `review` subcommand
- Session resume (`--resume-last`)
- Structured output schema (`--json-schema`)
- Progress reporting to Codex mid-run
