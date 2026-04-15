# claudecode-companion Delta Spec

## ADDED

### Basic task execution (read-only)
GIVEN the `claude` binary is available and authenticated
WHEN `claudecode-companion.mjs task "explain this file"` is run
THEN CC is spawned with `-p`, `--output-format stream-json`, `--bare`, and read-only `--allowedTools`
AND the CC response text is printed to stdout
AND the process exits with code 0

### Write-enabled task execution
GIVEN the `claude` binary is available and authenticated
WHEN `claudecode-companion.mjs task --write "refactor src/foo.js"` is run
THEN CC is spawned with `--allowedTools` that includes `Edit,Write,Bash`
AND CC is permitted to modify files in the working directory

### Read-only default blocks file writes
GIVEN `--write` is NOT passed
WHEN CC attempts to edit a file
THEN `Edit`, `Write`, and `Bash` are absent from `--allowedTools`
AND CC cannot modify files

### Prompt from stdin
GIVEN a prompt is piped via stdin (e.g. `echo "review this" | node claudecode-companion.mjs task`)
WHEN the script reads stdin
THEN the piped text is used as the prompt
AND CC is invoked with that prompt

### Prompt from file
GIVEN `--prompt-file path/to/prompt.txt` is passed
WHEN the script reads the file
THEN the file contents are used as the prompt
AND CC is invoked with that prompt

### Custom model
GIVEN `--model claude-opus-4-6` is passed
WHEN CC is spawned
THEN the `--model claude-opus-4-6` flag is forwarded to the `claude` invocation

### Custom max-turns
GIVEN `--max-turns 5` is passed
WHEN CC is spawned
THEN `--max-turns 5` is forwarded, capping CC to 5 turns

### JSON output mode
GIVEN `--json` is passed
WHEN CC completes
THEN a single JSON object is emitted to stdout with fields: `status` (number), `result` (string), `model` (string), `costUsd` (number)
AND no other text is written to stdout

### stderr relay
GIVEN CC writes to its stderr during execution
WHEN the companion relays output
THEN CC's stderr is forwarded directly to the companion's stderr

### CC binary not found
GIVEN `claude` is not on PATH
WHEN `claudecode-companion.mjs task "anything"` is run
THEN an error is thrown before any spawn attempt
AND the error message mentions that `claude` was not found and how to install it
AND the process exits with a non-zero code

### No prompt provided
GIVEN no prompt is passed via argv, stdin, or `--prompt-file`
WHEN `claudecode-companion.mjs task` is run
THEN an error is thrown before spawning CC
AND the error message describes how to provide a prompt

### Recursion guard blocks re-entry
GIVEN `CLAUDE_COMPANION_DEPTH` is set in the environment (i.e. this is a recursive call from CC)
WHEN `claudecode-companion.mjs task "anything"` is run
THEN an error is thrown immediately at entry
AND the process exits with a non-zero code
AND CC is never spawned

### Recursion guard is set on child
GIVEN `CLAUDE_COMPANION_DEPTH` is NOT set in the environment
WHEN CC is spawned
THEN `CLAUDE_COMPANION_DEPTH=1` is set in the child process's environment

### Non-zero exit code propagation
GIVEN CC exits with a non-zero exit code (e.g. 1)
WHEN the companion's close handler fires
THEN `process.exitCode` is set to that same non-zero code

### Spawn failure propagation
GIVEN a spawn error occurs (e.g. binary found but fails to launch)
WHEN `child.on('error')` fires
THEN the error message is written to stderr
AND `process.exitCode` is set to 1

### Working directory override
GIVEN `--cwd /some/path` is passed
WHEN CC is spawned
THEN the child process runs with `/some/path` as its working directory

### Help output
GIVEN `--help` is passed or no subcommand is given
WHEN the script runs
THEN usage text is printed to stdout describing the `task` subcommand and its flags
AND the process exits with code 0
