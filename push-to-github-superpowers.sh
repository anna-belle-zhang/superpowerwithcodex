#!/bin/bash
set -euo pipefail

# =============================================================================
# Push Superpowers Plugin Changes to GitHub
# =============================================================================
# This script commits and pushes superpowers plugin changes to GitHub
# Repository: https://github.com/anna-belle-zhang/superpowerwithcodex
# =============================================================================

# Configuration
REPO_PATH="/mnt/g/A/superpowers-main"
REPO_NAME="superpowerwithcodex"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# =============================================================================
# Step 0: Navigate to Repository
# =============================================================================
print_header "Step 0: Navigating to Superpowers Repository"

if [ ! -d "$REPO_PATH" ]; then
    print_error "Repository not found at $REPO_PATH"
    exit 1
fi

cd "$REPO_PATH"
print_success "Working directory: $(pwd)"

# =============================================================================
# Step 1: Verify Git Repository
# =============================================================================
print_header "Step 1: Verifying Git Repository"

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not a git repository"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "No remote configured")
print_info "Remote: $REMOTE_URL"

if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Not on main branch"
    print_info "Continuing on branch '$CURRENT_BRANCH'"
fi

# =============================================================================
# Step 2: Show Current Changes
# =============================================================================
print_header "Step 2: Current Changes"

echo "Modified files:"
git status --short

CHANGED_COUNT=$(git status --porcelain | wc -l)
print_info "Total changed files: $CHANGED_COUNT"

if [ "$CHANGED_COUNT" -eq 0 ]; then
    print_info "No local changes detected"
fi

# =============================================================================
# Step 3: Repository Information
# =============================================================================
print_header "Step 3: Repository Information"

cat <<EOF

Repository: $REPO_NAME
Path: $REPO_PATH
Remote: $REMOTE_URL

Key Components:
---------------
${CYAN}Skills System:${NC}
  - skills/                    # Skill definitions (TDD, brainstorming, etc.)
  - lib/skills-core.js         # Core skill discovery logic

${CYAN}Plugin System:${NC}
  - .claude-plugin/plugin.json      # Plugin metadata
  - .claude-plugin/marketplace.json # Marketplace configuration

${CYAN}Codex Integration:${NC}
  - codex-as-mcp-main/         # Codex MCP server for subagents
  - docs/codex-integration.md  # Integration documentation

${CYAN}Commands:${NC}
  - /superpowers:brainstorm    # Interactive design refinement
  - /superpowers:write-plan    # Create implementation plan
  - /superpowers:execute-plan  # Execute plan in batches

EOF

# =============================================================================
# Step 4: Stage Changes
# =============================================================================
print_header "Step 4: Staging Changes"

if [ -n "$(git status --porcelain)" ]; then
    print_info "Adding all changes..."
    git add -A

    echo ""
    echo "Staged files:"
    git diff --cached --stat
else
    print_info "No changes to stage"
fi

# =============================================================================
# Step 5: Create Commit
# =============================================================================
print_header "Step 5: Creating Commit"

if ! git diff --cached --quiet; then
    # Generate commit message
    if [ -n "${COMMIT_MESSAGE:-}" ]; then
        MSG="$COMMIT_MESSAGE"
    else
        # Auto-generate based on changed files
        SKILL_CHANGES=$(git diff --cached --name-only | grep -c "^skills/" || true)
        CODEX_CHANGES=$(git diff --cached --name-only | grep -c "^codex-as-mcp" || true)
        PLUGIN_CHANGES=$(git diff --cached --name-only | grep -c "^\.claude-plugin/" || true)

        if [ "$SKILL_CHANGES" -gt 0 ] && [ "$CODEX_CHANGES" -gt 0 ]; then
            MSG="feat: update skills and codex integration"
        elif [ "$SKILL_CHANGES" -gt 0 ]; then
            MSG="feat: update superpowers skills"
        elif [ "$CODEX_CHANGES" -gt 0 ]; then
            MSG="feat: update codex-as-mcp integration"
        elif [ "$PLUGIN_CHANGES" -gt 0 ]; then
            MSG="chore: update plugin configuration"
        else
            MSG="chore: update superpowers plugin"
        fi
    fi

    print_info "Creating commit: $MSG"
    git commit -m "$MSG"
    print_success "Commit created successfully"

    echo ""
    git --no-pager log -1 --stat
else
    print_info "No staged changes to commit"
fi

# =============================================================================
# Step 6: Push to Remote
# =============================================================================
print_header "Step 6: Pushing to GitHub"

print_info "Remote information:"
git remote -v

echo ""
print_info "Pushing to origin/$CURRENT_BRANCH..."
git push origin "$CURRENT_BRANCH"

print_success "Successfully pushed to GitHub!"

# =============================================================================
# Step 7: Summary
# =============================================================================
print_header "Step 7: Summary"

COMMIT_SHA=$(git rev-parse --short HEAD)
GITHUB_URL="https://github.com/anna-belle-zhang/superpowerwithcodex"

cat <<EOF

✅ Changes pushed successfully!

Commit: $COMMIT_SHA
Branch: $CURRENT_BRANCH
Remote: $REMOTE_URL

View commit: ${GITHUB_URL}/commit/$COMMIT_SHA

Installation:
-------------
# Via marketplace (once published):
/plugin marketplace add anna-belle-zhang/superpowerwithcodex
/plugin install superpowers@superpowerwithcodex

# Local development:
/plugin install file://$REPO_PATH

Verify:
-------
/help  # Should show superpowers commands

EOF

print_success "Superpowers plugin pushed to GitHub!"
