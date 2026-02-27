# Skill Marketplace Search Design

## Architecture
Skill-only approach. No new code. Claude uses the existing `WebFetch` tool to fetch the catalog JSON and filters results in-context. Two new files only.

## Components
- **`commands/search.md`** — Registers `/superpowerwithcodex:search`. YAML frontmatter + one instruction line delegating to the skill. Mirrors `commands/brainstorm.md` pattern.
- **`skills/search-marketplace/SKILL.md`** — Instructs Claude to parse the command input, fetch the catalog, filter entries, and render output.

## Data Flow
```
user: /superpowerwithcodex:search <query> --source <catalog-url>
  → skill parses query and --source flag
  → WebFetch GET <catalog-url>
  → filter plugins[] where name or description contains query (case-insensitive)
  → render matched cards OR empty/error message
```

## Card Format
```
Name:        <skill-name>
Description: <description>
Author:      <author>
Install:     /plugin install <name>@<marketplace>
```

## Error Handling
| Scenario | Message |
|---|---|
| Network failure / non-200 | `Could not reach marketplace at <url>. Check the URL and try again.` |
| No `plugins[]` in response | `Unexpected catalog format at <url>.` |
| No query argument | `Usage: /superpowerwithcodex:search <query> --source <catalog-url>` |
| No matches | `No skills found for '<query>'` |

## Dependencies
- `WebFetch` tool (built-in to Claude Code)
- Remote catalog JSON with a `plugins[]` array where each entry has `name`, `description`, `author`, and enough metadata to construct an install command
