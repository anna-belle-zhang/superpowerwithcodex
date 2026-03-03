# Installing Superpowerwithcodex for Codex

This is a private repo. Install via symlink from your local checkout — skills update instantly without any sync step.

## Installation

1. **Symlink local repo into Codex's skills directory**:
   ```bash
   ln -s /path/to/your/superpowerwithcodex ~/.codex/superpowerwithcodex
   ```
   Replace `/path/to/your/superpowerwithcodex` with the actual path where this repo lives on your machine.

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
