# Installing Superpowerwithcodex for Codex

Quick setup to enable superpowerwithcodex skills in Codex.

## Installation

1. **Clone superpowerwithcodex repository**:
   ```bash
   mkdir -p ~/.codex/superpowerwithcodex
   cd ~/.codex/superpowerwithcodex
   git clone https://github.com/anna-belle-zhang/superpowerwithcodex.git .
   ```

2. **Create personal skills directory**:
   ```bash
   mkdir -p ~/.codex/skills
   ```

3. **Update ~/.codex/AGENTS.md** to include this section:
   ```markdown
   ## Superpowerwithcodex System

   <EXTREMELY_IMPORTANT>
   You have superpowers. Superpowers teach you new skills and capabilities. RIGHT NOW run: `~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap` and follow the instructions it returns.
   </EXTREMELY_IMPORTANT>
   ```

## Verification

Test the installation:
```bash
~/.codex/superpowerwithcodex/.codex/superpowerwithcodex-codex bootstrap
```

You should see skill listings and bootstrap instructions. The system is now ready for use.
