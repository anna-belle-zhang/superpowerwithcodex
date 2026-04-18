# Installing Superpowerwithcodex for Codex

## Installation

1. **Clone the repo into Codex's skills directory**:
   ```bash
   git clone https://github.com/anna-belle-zhang/superpowerwithcodex ~/.codex/superpowerwithcodex
   ```
   Or clone anywhere and symlink:
   ```bash
   git clone https://github.com/anna-belle-zhang/superpowerwithcodex /path/to/superpowerwithcodex
   ln -s /path/to/superpowerwithcodex ~/.codex/superpowerwithcodex
   ```

2. **Create personal skills directory**:
   ```bash
   mkdir -p ~/.codex/skills
   ```

3. **Add to `~/.codex/AGENTS.md`**:
   ```markdown
   ## Superpowerwithcodex System

   <EXTREMELY_IMPORTANT>
   You have superpowerwithcodex. Superpowerwithcodex teaches you new skills and capabilities. RIGHT NOW run: `~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap` and follow the instructions it returns.
   </EXTREMELY_IMPORTANT>
   ```

4. **Enable Codex → Claude Code calling** (add to `~/.codex/AGENTS.md`):
   ```markdown
   ## Claude Code Companion

   You can call Claude Code headlessly from within your session using:
   ```bash
   node ~/.codex/superpowerwithcodex/.codex/scripts/claudecode-companion.mjs task "your prompt here"
   ```
   Flags:
   - `--write`              allow Claude Code to edit files (default: read-only)
   - `--model <model>`      override model (default: claude-sonnet-4-6)
   - `--max-turns <n>`      cap turns (default: 10)
   - `--json`               emit a single JSON envelope with {status, result, model, costUsd}
   - `--prompt-file <path>` read prompt from a file
   - `--cwd <path>`         run Claude Code in the given directory

   Use this when you need Claude Code to review, analyze, or implement something
   that benefits from a second high-reasoning agent's perspective.
   ```

## Verification

```bash
~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap
```

You should see skill listings and bootstrap instructions.

Verify the companion is available:
```bash
node ~/.codex/superpowerwithcodex/.codex/scripts/claudecode-companion.mjs --help
```

The system is now ready for use.

## Updating

```bash
cd ~/.codex/superpowerwithcodex && git pull
```
