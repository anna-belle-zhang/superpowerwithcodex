# Codex Integration Testing Setup

## Overview

Codex CLI runs inside a sandboxed Docker container with network blocked by default. For integration tests that hit external services (APIs, databases, Azure CLI), you must enable network access.

---

## Network Access Configuration

### Setup (One-Time)

Create or edit `~/.config/codex/config.toml`:

```toml
[sandbox.workspace_write]
network_access = true
```

This enables network for all Codex operations in `workspace-write` sandbox mode.

### Verify Configuration

Test that network access works:

```bash
codex e --full-auto "curl -s https://api.github.com/zen"
```

**Expected:** Returns a GitHub zen quote (e.g., "Approachable is better than simple.")

**If you see:** `network is unreachable` or `connection refused` → Config not applied, check file path and restart terminal.

---

## Sandbox Modes

| Mode | Network | Filesystem | Use Case |
|------|---------|------------|----------|
| `workspace-read` | Blocked | Read-only | Safe exploration |
| `workspace-write` | Configurable | Project dir only | Development (default) |
| `full-auto` | Configurable | Project dir only | Autonomous execution |

The `network_access = true` setting in config applies to `workspace-write` and `full-auto` modes.

---

## Alternative: Per-Command Network

If you prefer explicit control per execution (not recommended for Ralph workflows):

```bash
codex e --full-auto \
  --sandbox workspace-write \
  -c 'sandbox_workspace_write.network_access=true' \
  "your prompt here"
```

---

## WSL-Specific Setup

### Docker Daemon

Ensure Docker is running in WSL:

```bash
sudo service docker start
```

Or if using Docker Desktop, ensure WSL integration is enabled in Docker Desktop settings.

### Docker Network Bridge

If network issues persist in WSL, verify Docker networking:

```bash
docker network ls
docker run --rm alpine ping -c 1 google.com
```

---

## Integration with Ralph-Codex-E2E Workflow

When using the Ralph Wiggum loop with Codex for integration tests:

1. **Global config is required** - Ralph loops many times, per-command flags are impractical
2. **Codex handles**: Unit tests + Integration tests (network enabled)
3. **Claude handles**: E2E tests (project-specific)

See: `docs/plans/2026-01-25-ralph-codex-e2e-design.md`

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `network is unreachable` | Network disabled | Add config to `~/.config/codex/config.toml` |
| `docker: command not found` | Docker not installed | Install Docker Desktop or `apt install docker.io` |
| `permission denied` on docker | Not in docker group | `sudo usermod -aG docker $USER` then re-login |
| `Cannot connect to Docker daemon` | Daemon not running | `sudo service docker start` |
| Config file ignored | Wrong path | Must be `~/.config/codex/config.toml` (not `.codex/`) |
| Azure CLI auth fails | Token not in container | Run `az login` inside Codex or mount credentials |

### Azure CLI in Codex

For `az` commands to work, Codex needs Azure credentials. Options:

1. **Device code auth** (recommended):
   ```bash
   codex e --full-auto "az login --use-device-code"
   ```

2. **Service principal** (CI/CD):
   ```bash
   codex e --full-auto "az login --service-principal -u $APP_ID -p $SECRET --tenant $TENANT"
   ```

---

## Quick Reference

```bash
# One-time setup
mkdir -p ~/.config/codex
cat > ~/.config/codex/config.toml << 'EOF'
[sandbox.workspace_write]
network_access = true
EOF

# Verify
codex e --full-auto "curl -s https://api.github.com/zen"

# Run integration tests
codex e --full-auto "npm run test:integration"
```
