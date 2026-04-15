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
  '--bare',                           // skip hooks/plugins/CLAUDE.md auto-load
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

## Recursion Guard

Set `CLAUDE_COMPANION_DEPTH=1` in the child's env. At entry, check:

```js
if (process.env.CLAUDE_COMPANION_DEPTH) {
  throw new Error('Recursive claudecode-companion call detected. Aborting.');
}
```

This prevents CC from calling back into this companion in a loop.

## Output Handling

`stream-json` emits JSONL — one JSON object per line. Event types:

- `assistant` — streaming text chunks (relay to stdout in non-`--json` mode)
- `result` — final result with `result` field and `cost_usd`
- `system` — metadata (ignore or log to stderr)

**Non-`--json` mode:** relay `assistant` text as it arrives; print final `result.result` at close.

**`--json` mode:** buffer everything, emit one envelope at close:
```json
{ "status": 0, "result": "...", "model": "...", "costUsd": 0.0012 }
```

**stderr:** always relay `child.stderr` directly to `process.stderr`.

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
- `--bare` prevents CLAUDE.md and plugins from expanding the tool surface unexpectedly
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
       ├─ spawn: claude -p "..." --output-format stream-json --bare ...
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
