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
   You have superpowers. Superpowers teach you new skills and capabilities. RIGHT NOW run: `~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap` and follow the instructions it returns.
   </EXTREMELY_IMPORTANT>
   ```

## Verification

```bash
~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap
```

You should see skill listings and bootstrap instructions. The system is now ready for use.

## Updating

```bash
cd ~/.codex/superpowerwithcodex && git pull
```
