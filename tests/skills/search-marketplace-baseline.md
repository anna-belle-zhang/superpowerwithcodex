# Search Marketplace — Baseline Behavior (No Skill)

## Scenario Tested

`/superpowerwithcodex:search tdd --source https://example.com/catalog.json`

Catalog returned 2 plugins: `test-driven-development` (description contains "TDD"), `brainstorming` (no match).

## What the Agent Did (Verbatim)

- Used WebFetch with the `--source` URL ✅
- Parsed `--source` flag correctly ✅
- Filtered by "tdd" — matched `test-driven-development`, excluded `brainstorming` ✅
- Matched "TDD" in description despite lowercase query (case-insensitive naturally) ✅
- Included an Install field: `/plugin install test-driven-development@superpowers-marketplace` ✅

## Deviations from Expected Spec Format

| Expected | Actual (baseline) | Issue |
|----------|-------------------|-------|
| `Name:        test-driven-development` | `**Name:** test-driven-development` | Bold markdown headers instead of plain padded text |
| No Version field | Included `Version: 1.0.0` | Extra field not in spec |
| Exact label spacing | Variable spacing | Format not enforced |

## Untested Error Scenarios (No Skill)

These scenarios were NOT tested in baseline — skill must enforce them:
- No results → expected `No skills found for '<query>'` (unknown baseline behavior)
- Network failure → expected specific error message (unknown baseline behavior)
- Malformed catalog (no `plugins[]`) → expected specific error message (unknown baseline behavior)
- Missing query argument → expected usage hint (unknown baseline behavior)

## Conclusion

The agent naturally does ~80% of the right thing for the happy path. The skill must enforce:
1. **Exact card format** — plain text labels with consistent padding, not bold markdown
2. **No extra fields** — only Name, Description, Author, Install
3. **Specific error messages** — for network failure, malformed catalog, no results, missing query
4. **Stop on error** — explicit instruction to stop after printing error, not continue
