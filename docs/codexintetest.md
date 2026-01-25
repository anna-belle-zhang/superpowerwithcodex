# Codex Integration Testing Setup

## Overview

Codex CLI runs inside a sandboxed Docker container with network blocked by default. For integration tests that hit external services (APIs, databases, Azure CLI), you must enable network access.

---

## Network Access Configuration

### Setup (One-Time)

Create or edit `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
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
| `network is unreachable` | Network disabled | Add config to `~/.codex/config.toml` |
| `docker: command not found` | Docker not installed | Install Docker Desktop or `apt install docker.io` |
| `permission denied` on docker | Not in docker group | `sudo usermod -aG docker $USER` then re-login |
| `Cannot connect to Docker daemon` | Daemon not running | `sudo service docker start` |
| Config file ignored | Wrong path | Must be `~/.codex/config.toml` (not `~/.config/codex/`) |
| Config section ignored | Wrong TOML syntax | Use `[sandbox_workspace_write]` (underscores, not dots) |
| `python.exe: Permission denied` | Using Windows az CLI | Install native Linux az: `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| `Permission denied: ~/.azure/commands/` | Sandbox can't write logs | Use `export AZURE_CONFIG_DIR=/tmp/azure` workaround |
| Azure CLI auth fails | Token expired or not copied | Run `az login` in WSL, then copy `~/.azure` to `/tmp/azure` |

### Install Azure CLI in WSL (Required)

The Windows Azure CLI (`/mnt/c/.../az`) does **not** work inside Codex sandbox because:
- It tries to execute `python.exe` which the Linux sandbox blocks
- Permission denied errors on Windows binaries

**Install native Linux Azure CLI:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Verify installation:**
```bash
which az        # Should show /usr/bin/az
az --version    # Should show azure-cli 2.x
```

**Credentials are shared:** The `~/.azure/` directory stores tokens that work for both Windows and Linux CLI versions. If you're already logged in via Windows `az`, no new login is needed.

### Azure CLI in Codex Sandbox

For `az` commands to work inside Codex sandbox, you need credentials and a writable config directory.

**Sandbox workaround** (copy credentials to writable location):
```bash
export AZURE_CONFIG_DIR=/tmp/azure
rm -rf /tmp/azure
cp -r ~/.azure /tmp/azure
chmod -R 700 /tmp/azure
az group list --query "[].name" -o tsv
```

**Authentication options:**

1. **Use existing WSL credentials** (recommended):
   - Run `az login` in your normal WSL terminal
   - Credentials in `~/.azure/` are copied to sandbox via the workaround above

2. **Device code auth** (if no existing login):
   ```bash
   codex e --full-auto "az login --use-device-code"
   ```

3. **Service principal** (CI/CD):
   ```bash
   codex e --full-auto "az login --service-principal -u $APP_ID -p $SECRET --tenant $TENANT"
   ```

---

## Quick Reference

```bash
# One-time setup
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
[sandbox_workspace_write]
network_access = true
EOF

# Verify
codex e --full-auto "curl -s https://api.github.com/zen"

# Run integration tests
codex e --full-auto "npm run test:integration"
```

---

## Lessons Learned

Common pitfalls discovered during setup:

### Config File Path
- **Wrong:** `~/.config/codex/config.toml`
- **Correct:** `~/.codex/config.toml`

### TOML Section Names
- **Wrong:** `[sandbox.workspace_write]` (dots)
- **Correct:** `[sandbox_workspace_write]` (underscores)

### Windows vs Linux CLI in WSL
| CLI Location | Works in Codex Sandbox? | Reason |
|--------------|------------------------|--------|
| `/mnt/c/.../az` (Windows) | No | Sandbox blocks `python.exe` execution |
| `/usr/bin/az` (Linux) | Yes | Native Linux binary runs normally |

### Azure Credentials
- `~/.azure/` stores MSAL tokens shared between Windows and Linux CLI
- `az account show` works offline (reads cached subscription info)
- `az group list` and other API calls require network + valid tokens
- Sandbox can't write to `~/.azure/commands/` for logging → use `AZURE_CONFIG_DIR=/tmp/azure`

### MCP Subagent Server
- Config changes require **Claude Code restart** for MCP server to reload
- The `codex-as-mcp` server spawns fresh Codex processes that read `~/.codex/config.toml`

### Verification Commands
```bash
# Test network in sandbox
codex e --full-auto "curl -s https://api.github.com/zen"

# Test Azure CLI in sandbox (with workaround)
codex e --full-auto "export AZURE_CONFIG_DIR=/tmp/azure && cp -r ~/.azure /tmp/azure && az group list -o table | head -5"
```
