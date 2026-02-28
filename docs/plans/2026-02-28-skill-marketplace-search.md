---
execution-strategy: codex-subagents
created: 2026-02-28
codex-available: true
specs-dir: docs/specs/skill-marketplace-search/
---

# Skill Marketplace Search Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `/superpowerwithcodex:search <query> --source <catalog-url>` slash command that fetches a remote marketplace catalog and displays matching skills as detailed cards.

**Architecture:** Skill-only approach — two new markdown files. A `commands/search.md` registers the slash command; `skills/search-marketplace/SKILL.md` instructs Claude to use `WebFetch` to fetch the catalog JSON, filter `plugins[]` by query (case-insensitive substring on name + description), and render results as cards. No production code, no dependencies.

**Tech Stack:** Markdown (YAML frontmatter), Claude `WebFetch` tool

**Specs:** `docs/specs/skill-marketplace-search/`

---

## Mock Catalog JSON (used in all pressure tests)

Save this as a reference — paste into subagent prompts to simulate `WebFetch` responses:

```json
{
  "name": "superpowers-marketplace",
  "plugins": [
    {
      "name": "test-driven-development",
      "description": "Use when implementing any feature or bugfix - enforces RED-GREEN-REFACTOR TDD cycle",
      "author": { "name": "obra" },
      "version": "1.0.0"
    },
    {
      "name": "brainstorming",
      "description": "Use when creating or developing ideas before writing code",
      "author": { "name": "obra" },
      "version": "1.0.0"
    },
    {
      "name": "condition-based-waiting",
      "description": "Use when tests have race conditions or timing dependencies",
      "author": { "name": "obra" },
      "version": "1.0.0"
    }
  ]
}
```

---

### Task 1: Run Baseline Pressure Scenario (RED Phase)

**Purpose:** Establish what Claude does WITHOUT the skill before writing it. Iron Law: no skill without a failing test first.

**Files:**
- Create: `tests/skills/search-marketplace-baseline.md` (document baseline results here)

**Step 1: Run baseline subagent — no skill loaded**

Dispatch a subagent with this prompt (do NOT include any search-marketplace skill):

```
You are a Claude Code assistant. The user has run:

  /superpowerwithcodex:search tdd --source https://example.com/catalog.json

There is no search-marketplace skill installed. Respond as you naturally would.
Assume WebFetch returns this catalog JSON:
{
  "name": "superpowers-marketplace",
  "plugins": [
    { "name": "test-driven-development", "description": "Use when implementing any feature or bugfix - enforces RED-GREEN-REFACTOR TDD cycle", "author": { "name": "obra" }, "version": "1.0.0" },
    { "name": "brainstorming", "description": "Use when creating or developing ideas before writing code", "author": { "name": "obra" }, "version": "1.0.0" }
  ]
}
```

**Step 2: Document exact failures**

In `tests/skills/search-marketplace-baseline.md`, record verbatim:
- Did it use WebFetch?
- Did it parse and filter the catalog?
- Did it format cards with Name/Description/Author/Install fields?
- Did it handle the `--source` flag correctly?
- What rationalizations or wrong paths did it take?

**Step 3: Commit baseline**

```bash
git add tests/skills/search-marketplace-baseline.md
git commit -m "test: document baseline behavior for search-marketplace skill"
```

---

### Task 2: Create `commands/search.md`

**Files:**
- Create: `commands/search.md`

**Scenarios:**
| ID | Scenario | Source |
|----|----------|--------|
| S1 | GIVEN plugin installed WHEN user types `/superpowerwithcodex:search` THEN search-marketplace skill activates | search-command-delta.md |

**Step 1: Create the command file**

`commands/search.md`:
```markdown
---
description: Search remote marketplace catalog for skills by keyword
---

Use and follow the search-marketplace skill exactly as written
```

**Step 2: Verify structure matches existing commands**

```bash
diff <(head -5 commands/brainstorm.md) <(head -5 commands/search.md)
# Expected: same YAML frontmatter + instruction pattern
```

**Step 3: Commit**

```bash
git add commands/search.md
git commit -m "feat: add search slash command"
```

---

### Task 3: Create `skills/search-marketplace/SKILL.md`

**Files:**
- Create: `skills/search-marketplace/SKILL.md`

**Scenarios (all 6 from delta spec):**
| ID | Scenario | Source |
|----|----------|--------|
| S2 | GIVEN valid URL + matching query WHEN search runs THEN detailed cards shown | search-marketplace-skill-delta.md |
| S3 | GIVEN skill with "TDD" in description WHEN searching "tdd" THEN case-insensitive match | search-marketplace-skill-delta.md |
| S4 | GIVEN valid URL + no matching query WHEN search runs THEN `No skills found for '<query>'` | search-marketplace-skill-delta.md |
| S5 | GIVEN unreachable URL WHEN search runs THEN error message | search-marketplace-skill-delta.md |
| S6 | GIVEN JSON without `plugins[]` WHEN search runs THEN malformed catalog error | search-marketplace-skill-delta.md |
| S7 | GIVEN no query argument WHEN search runs THEN usage hint printed | search-marketplace-skill-delta.md |

**Step 1: Create skill directory**

```bash
mkdir -p skills/search-marketplace
```

**Step 2: Write the skill file**

`skills/search-marketplace/SKILL.md`:
```markdown
---
name: search-marketplace
description: Use when user runs /superpowerwithcodex:search to find skills in a remote marketplace catalog before installing - fetches catalog JSON from --source URL, filters plugins by query against name and description (case-insensitive), displays results as detailed cards with install command
---

# Search Marketplace

Search a remote marketplace catalog for skills matching a query.

**Announce at start:** "Searching marketplace for '<query>'..."

## Usage

`/superpowerwithcodex:search <query> --source <catalog-url>`

## Process

### Step 1: Parse Input

From the command input, extract:
- `<query>`: all text before `--source`, trimmed
- `<catalog-url>`: all text after `--source`, trimmed

If `<query>` is empty after trimming, print:
```
Usage: /superpowerwithcodex:search <query> --source <catalog-url>
```
Stop. Do not proceed.

### Step 2: Fetch Catalog

Use WebFetch to GET `<catalog-url>`.

If the request fails or the URL is unreachable, print:
```
Could not reach marketplace at <catalog-url>. Check the URL and try again.
```
Stop. Do not proceed.

### Step 3: Validate and Filter

Parse the response as JSON. If the parsed JSON has no `plugins` array, print:
```
Unexpected catalog format at <catalog-url>.
```
Stop. Do not proceed.

Filter `plugins` entries where `name` OR `description` contains `<query>` as a **case-insensitive** substring. "tdd" must match "TDD", "Tdd", "tdd".

### Step 4: Display Results

If no entries match, print exactly:
```
No skills found for '<query>'
```

For each matching entry, print a card in this exact format:
```
Name:        <plugins[i].name>
Description: <plugins[i].description>
Author:      <plugins[i].author.name>
Install:     /plugin install <plugins[i].name>@<root-level catalog name field>
```

Separate multiple cards with a blank line.
```

**Step 3: Verify frontmatter character count**

```bash
head -5 skills/search-marketplace/SKILL.md | wc -c
# Expected: under 1024 characters total for name + description fields
```

**Step 4: Commit**

```bash
git add skills/search-marketplace/SKILL.md
git commit -m "feat: add search-marketplace skill"
```

---

### Task 4: Run All 6 Pressure Scenarios (GREEN Phase)

**Purpose:** Verify all delta spec scenarios pass with the skill loaded.

**Files:**
- Create: `tests/skills/search-marketplace-green.md` (document results)

Run each scenario as a subagent with the skill loaded. Paste the full `skills/search-marketplace/SKILL.md` content into each subagent prompt.

---

**Scenario S2 — Matching cards:**

Subagent prompt:
```
You are Claude Code. The following skill is loaded:
[paste full contents of skills/search-marketplace/SKILL.md]

The user ran: /superpowerwithcodex:search tdd --source https://example.com/catalog.json

WebFetch returns:
{
  "name": "superpowers-marketplace",
  "plugins": [
    { "name": "test-driven-development", "description": "Use when implementing any feature or bugfix - enforces RED-GREEN-REFACTOR TDD cycle", "author": { "name": "obra" }, "version": "1.0.0" },
    { "name": "brainstorming", "description": "Use when creating or developing ideas before writing code", "author": { "name": "obra" }, "version": "1.0.0" }
  ]
}

Follow the skill exactly.
```

Expected output:
```
Searching marketplace for 'tdd'...

Name:        test-driven-development
Description: Use when implementing any feature or bugfix - enforces RED-GREEN-REFACTOR TDD cycle
Author:      obra
Install:     /plugin install test-driven-development@superpowers-marketplace
```

---

**Scenario S3 — Case-insensitive match:**

Same as S2 but query is `"tdd"` (lowercase) and catalog description contains `"TDD"` (uppercase).
Expected: `test-driven-development` still appears in results.

---

**Scenario S4 — No results:**

Subagent prompt: same setup but query is `"nonexistent-xyz-12345"`.

Expected output:
```
Searching marketplace for 'nonexistent-xyz-12345'...
No skills found for 'nonexistent-xyz-12345'
```

---

**Scenario S5 — Network failure:**

Subagent prompt: skill loaded. User ran search. Tell the subagent: "WebFetch to https://bad-url.invalid fails with a connection error."

Expected output:
```
Searching marketplace for 'tdd'...
Could not reach marketplace at https://bad-url.invalid. Check the URL and try again.
```

---

**Scenario S6 — Malformed catalog:**

Subagent prompt: WebFetch returns `{ "version": "1.0" }` (no `plugins` array).

Expected output:
```
Searching marketplace for 'tdd'...
Unexpected catalog format at <url>.
```

---

**Scenario S7 — Missing query:**

Subagent prompt: user ran `/superpowerwithcodex:search --source https://example.com/catalog.json` (no query text).

Expected output:
```
Usage: /superpowerwithcodex:search <query> --source <catalog-url>
```

---

**Step: Document results**

In `tests/skills/search-marketplace-green.md`, record pass/fail for each scenario. Note any unexpected behavior verbatim.

**Step: Commit results**

```bash
git add tests/skills/search-marketplace-green.md
git commit -m "test: document green phase results for search-marketplace skill"
```

---

### Task 5: Close Loopholes (REFACTOR Phase) and Final Commit

**Purpose:** Fix any scenario failures from Task 4. Iterate until all 6 pass.

**Step 1: For each failing scenario**

Identify the rationalization or gap. Edit `skills/search-marketplace/SKILL.md` to add explicit counter or clarification. Re-run the failing scenario.

**Common loopholes to watch for:**
- Skipping `WebFetch` and hallucinating catalog contents
- Not applying case-insensitive matching (matching "tdd" only, missing "TDD")
- Constructing the install command from wrong field (using URL instead of catalog name)
- Printing partial cards (missing Author or Install field)
- Continuing after an error instead of stopping

**Step 2: Verify word count stays reasonable**

```bash
wc -w skills/search-marketplace/SKILL.md
# Target: under 500 words (frequently-loaded skills aim for under 200, but this is a technique skill)
```

**Step 3: Final commit**

```bash
git add skills/search-marketplace/SKILL.md tests/skills/
git commit -m "refactor: close skill loopholes, all 6 scenarios passing"
```
