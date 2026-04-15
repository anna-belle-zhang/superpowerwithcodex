# claudecode-companion Design

## Architecture

Single Node ESM script (`claudecode-companion.mjs`) alongside `codex-companion.mjs` in
`repos/codex-plugin-cc/plugins/codex/scripts/`. Reuses existing lib utilities — no new
dependencies. Foreground-only in v1.

## Components

| Component | Responsibility |
|-----------|---------------|
| `claudecode-companion.mjs` | CLI entry, arg parsing, preflight, spawn, output relay |
| `lib/args.mjs` | Arg parsing (`parseArgs`, `splitRawArgumentString`) — reused as-is |
| `lib/process.mjs` | Binary preflight (`binaryAvailable`) — reused as-is |
| `lib/fs.mjs` | Stdin reading (`readStdinIfPiped`) — reused as-is |

## Claude Invocation

```
claude -p <prompt>
  --output-format stream-json
  --bare
  --max-turns <n>
  --model <model>
  --allowedTools Read,Glob,Grep[,Edit,Write,Bash] (,WebFetch,WebSearch)
```

- `--bare`: skips hooks, plugins, CLAUDE.md auto-load — required for automation hygiene
- `--output-format stream-json`: JSONL stream, one typed event per line
- `--allowedTools`: explicit allowlist; no blanket bypass flags

## Data Flow

```
Codex session
  └─ claudecode-companion.mjs task [prompt]
       ├─ binaryAvailable('claude') preflight
       ├─ recursion guard (CLAUDE_COMPANION_DEPTH)
       ├─ spawn claude -p ... --output-format stream-json --bare
       │    ├─ JSONL stdout → parse events → relay to caller
       │    └─ stderr → relay directly to process.stderr
       └─ child exit code → process.exitCode
```

## Output Modes

**Default (text):** relay `assistant` event text as it streams; print final `result.result` on close.

**`--json`:** buffer all events; emit one envelope on close:
```json
{ "status": 0, "result": "...", "model": "...", "costUsd": 0.0012 }
```

## Error Handling

| Scenario | Handling |
|----------|---------|
| `claude` not on PATH | `binaryAvailable` preflight throws before spawn |
| No prompt provided | Throw with usage hint before spawning |
| Recursion detected | Throw at entry (check `CLAUDE_COMPANION_DEPTH`) |
| Spawn failure | `child.on('error')` → stderr + `process.exitCode = 1` |
| Non-zero CC exit | `child.on('close', code)` → `process.exitCode = code ?? 1` |

## Security Model

- Read-only by default (`Read,Glob,Grep,WebFetch,WebSearch`)
- `--write` explicitly adds `Edit,Write,Bash`
- `--bare` prevents unexpected tool surface expansion via CLAUDE.md/plugins
- `--max-turns` caps runaway sessions (default: 10)
- `CLAUDE_COMPANION_DEPTH=1` set in child env; checked at entry to block recursion

## Dependencies

- `lib/args.mjs` — existing, no changes
- `lib/process.mjs` — existing, no changes
- `lib/fs.mjs` — existing, no changes
- `claude` CLI — must be on PATH and authenticated
