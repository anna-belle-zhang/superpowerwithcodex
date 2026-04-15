## Plan
- [x] Task 1: CLI surface, help, prompt sourcing, binary checks, and basic read-only task execution
  RED: added failing coverage for help, missing prompt, missing binary, argv/stdin/file prompts, and read-only task spawning.
  GREEN: implemented `claudecode-companion.mjs` task mode with prompt resolution, read-only defaults, help output, and streamed assistant text handling.
- [x] Task 2: Write mode, forwarded spawn options, working directory handling, and recursion guards
  RED: added coverage for `--write`, `--model`, `--max-turns`, `--cwd`, recursion blocking, child-depth env propagation, and Windows launch behavior.
  GREEN: verified forwarded flags, child env protection, working-directory override, and exported Windows launch helper behavior.
- [x] Task 3: Stream handling, JSON output, stderr relay, and failure/exit propagation
  RED: added coverage for `--json`, stderr passthrough, non-zero child exits, and spawn-error propagation.
  GREEN: implemented final JSON envelope output, direct stderr relay, result/cost extraction, and exit/error status propagation.

## Issues
- The task instructions require this `progress.md` outside `repos/codex-plugin-cc/`; all other code and test changes stay inside `repos/codex-plugin-cc/`.
- The spec is explicit enough to treat the dispatch as pre-approved design for the TDD workflow.

## Commits
(empty)
