# Technical Debt

## Build Commands
**Build command:** echo "No build needed"
**Test command:** pytest tests/

## Technical Debt

### DEBT-1: Remove skill-marketplace-search feature
**What:**
- `skills/search-marketplace/SKILL.md`
- `commands/search.md`
- `docs/specs/skill-marketplace-search/` (entire directory)
- `tests/skills/search-marketplace-baseline.md`
- `tests/skills/search-marketplace-green.md`

**Why:** Feature not useful - marketplace search functionality not needed

**Replaced by:** N/A (feature removal, not replacement)

**Verification:** Run `pytest tests/` - all tests should pass after removal

**Source:** Manual decision (user request)
