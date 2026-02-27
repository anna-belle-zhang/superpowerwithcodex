# Skill Marketplace Search Design

## Problem

Users cannot search the remote marketplace catalog before installing a skill. Discovery requires browsing externally or guessing skill names.

## Solution

A new slash command `/superpowerwithcodex:search <query> --source <catalog-url>` that fetches a remote marketplace catalog, filters by query against name and description, and displays matching skills as detailed cards.

## Architecture

Skill-only approach: a new `search-marketplace` skill instructs Claude to use `WebFetch` to pull the catalog JSON and filter results in-context. No new code, no local state, no caching.

Two new files:
- `commands/search.md` — registers the slash command
- `skills/search-marketplace/SKILL.md` — fetch, filter, display logic

## Components

### `commands/search.md`
YAML frontmatter + one instruction line delegating to the skill. Follows the same pattern as `commands/brainstorm.md`.

### `skills/search-marketplace/SKILL.md`
When triggered, Claude:
1. Parses `<query>` and `--source <catalog-url>` from the command input
2. Uses `WebFetch` to GET the catalog JSON at the provided URL
3. Filters `plugins[]` entries where `name` or `description` contains the query (case-insensitive substring match)
4. Renders each match as a detailed card
5. Prints empty/error messages as appropriate

## Data Flow

```
user: /superpowerwithcodex:search tdd --source https://example.com/catalog.json
  → skill parses query="tdd", url="https://example.com/catalog.json"
  → WebFetch GET https://example.com/catalog.json
  → filter plugins[] by "tdd" in name or description
  → render matching cards
```

## Result Format

Each matching skill rendered as:
```
Name:        test-driven-development
Description: Use when implementing any feature or bugfix...
Author:      obra
Install:     /plugin install test-driven-development@superpowers-marketplace
```

## Error Handling

| Scenario | Output |
|---|---|
| Network failure / non-200 | `Could not reach marketplace at <url>. Check the URL and try again.` |
| Malformed catalog (no `plugins[]`) | `Unexpected catalog format at <url>.` |
| No query provided | `Usage: /superpowerwithcodex:search <query> --source <catalog-url>` |
| No matches | `No skills found for '<query>'` |

No retry, no fuzzy fallback.

## Testing

Skill tested with subagents per `writing-skills` methodology before deployment:

- **Scenario 1:** Valid URL + matching query → detailed card output
- **Scenario 2:** Valid URL + non-matching query → silent empty message, no hallucinated results
- **Scenario 3:** Bad URL → error message, no crash
- **Scenario 4:** Missing query → usage hint printed

## Out of Scope

- Local catalog caching
- Fuzzy/partial matching beyond substring
- Installing directly from search results
- Searching installed/local skills
