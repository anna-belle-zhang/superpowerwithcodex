# claudecode-companion Proposal

## Intent

`codex-companion.mjs` lets Claude Code call Codex. This feature adds the symmetric
counterpart: `claudecode-companion.mjs` lets Codex call Claude Code headlessly — mirroring
the existing pattern in the opposite direction. Codex can delegate analysis, review, or
implementation tasks to CC without leaving its session.

## Scope

**In scope:**
- Single `task` subcommand: spawn `claude -p <prompt>` as a subprocess
- Read-only by default; `--write` opts in to file mutation
- Flags: `--model`, `--max-turns`, `--json`, `--prompt-file`, `--cwd`
- Prompt from argv, `--prompt-file`, or piped stdin
- Auth/binary preflight before spawning
- Recursion guard via `CLAUDE_COMPANION_DEPTH` env var
- Exit code propagation from CC to caller
- `stream-json` JSONL output parsing and relay
- Windows support (`claude.cmd`, `shell: true`)

**Out of scope:**
- Background/detach mode and job tracking
- `review` or `adversarial-review` subcommands
- Session resume (`--resume-last`)
- Structured output schema (`--json-schema`)
- Progress reporting to Codex mid-run

## Impact

- **Users affected:** Codex users with `codex-plugin-cc` installed
- **Systems affected:** Adds one new script to `repos/codex-plugin-cc/plugins/codex/scripts/`; no changes to existing scripts
- **Risk:** Low — additive only, no modifications to existing code

## Success Criteria

- [ ] `node claudecode-companion.mjs task "explain this file"` runs CC and returns output
- [ ] Read-only mode prevents CC from writing files without `--write`
- [ ] Missing `claude` binary produces a clear error before any spawn attempt
- [ ] Recursive invocation (CC calling companion back) is blocked by env guard
- [ ] Non-zero CC exit code propagates to the companion's exit code
- [ ] `--json` flag emits a single JSON envelope with `status`, `result`, `costUsd`
- [ ] Works on Windows (`claude.cmd`, `shell: true`)
