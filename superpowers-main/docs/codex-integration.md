# Codex Integration Guide

Superpowers can optionally use Codex subagents for implementation while keeping Claude responsible for planning, tests, and review.

## Overview

**Recommended workflow:** Claude writes tests (TDD) → Codex implements within file boundaries → Claude runs tests + reviews → retry chain on failures.

This is implemented as:
- Skill: `superpowers:codex-subagent-driven-development`
- Wrapper library: `superpowers-main/lib/codex-integration.js`

## Prerequisites

### 1. Install Codex CLI

```bash
npm install -g @openai/codex@latest
codex login
codex --version
```

### 2. Configure MCP server

Add a `codex-subagent` server to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "codex-subagent": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}
```

If you are developing locally from this meta-workspace (no network installs), you can point the server command at the checked-in source in `codex-as-mcp-main/` instead of `@latest`.

### 3. Verify configuration

Run the Superpowers library test that validates the availability check:

```bash
bash superpowers-main/tests/opencode/run-tests.sh --test test-codex-integration.sh
```

## Using Codex Subagents

1. Create a design + plan using the normal flow:
   - `superpowers:brainstorming`
   - `superpowers:writing-plans`

2. In the execution handoff, choose:
   - **Codex subagents** (default when available)

3. Execute with:
   - `superpowers:codex-subagent-driven-development`

## File Boundaries (Hard Rule)

When dispatching Codex for implementation, always provide explicit boundaries:
- **Implement in:** only files Codex may modify
- **Read only:** tests, configs, lockfiles, docs that must not be changed

After implementation, verify boundaries via `git diff --name-only` before committing.

## Retry Chain

When tests fail or review issues arise:
1. Codex retry 1: send failing output + focused guidance
2. Codex retry 2: add explicit research guidance + retry
3. Claude fix attempts: implement/research manually
4. Escalate to human: revise plan or fix interactively

## Troubleshooting

**Codex not available**
- Missing `.mcp.json`
- Missing `mcpServers.codex-subagent`
- `codex` not on PATH / not authenticated

**Boundary violations**
- If Codex touches read-only files, revert those changes and retry with stricter boundary instructions.

