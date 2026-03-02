# Skill Document Tests Delta Spec

## ADDED

### S1 — Ralph Loop Command Construction
GIVEN the ralph-codex-e2e skill is loaded and a plan file path is provided
WHEN the agent is asked to start the Ralph-Codex-E2E workflow
THEN the agent constructs a `/ralph-loop` command that includes: the plan file path, per-task Codex phase steps, per-task Claude E2E phase steps, `--max-iterations` flag, and `--completion-promise "DONE"`

### S2 — Prerequisites Verification
GIVEN the ralph-codex-e2e skill is loaded and `~/.codex/config.toml` is missing or lacks `[sandbox_workspace_write] network_access = true`
WHEN the agent is asked to start the workflow
THEN the agent identifies the missing prerequisite and instructs the user to configure it before proceeding

### S3 — When-Not-To-Use Routing
GIVEN the ralph-codex-e2e skill is loaded
WHEN the user states they need human review between tasks
THEN the agent recommends `codex-subagent-driven-development` instead of ralph-codex-e2e and does not proceed with the Ralph loop

### S4 — E2E Strategy Detection (Playwright)
GIVEN the ralph-codex-e2e skill is loaded and the project contains `playwright.config.ts`
WHEN the agent selects the E2E strategy
THEN the agent selects Playwright browser tests (`npx playwright test`) as the E2E command

### S4b — E2E Strategy Detection (API)
GIVEN the ralph-codex-e2e skill is loaded and the project contains `openapi.yaml` but no Playwright/Cypress config
WHEN the agent selects the E2E strategy
THEN the agent selects API E2E (curl/httpie) as the E2E strategy, not bash default

### S5 — Retry Chain Escalation
GIVEN the ralph-codex-e2e skill is loaded and E2E tests have failed twice and Claude has retried twice
WHEN the agent evaluates next steps
THEN the agent lets Ralph loop again (does not commit with failing tests and does not declare success)

### S6 — Post-Loop Verification Steps
GIVEN the ralph-codex-e2e skill is loaded, Ralph has exited with "DONE", and `docs/specs/<feature>/` exists
WHEN the agent handles loop completion
THEN the agent runs `superpowers:verify-specs` before `superpowers:finishing-a-development-branch` and does not skip either step
