---
name: search-marketplace
description: Use when user runs /superpowerwithcodex:search to find skills in a remote marketplace catalog before installing - fetches catalog JSON from --source URL, filters plugins by query against name and description (case-insensitive), displays results as detailed cards with install command
---

# Search Marketplace

Search a remote marketplace catalog for skills matching a query.

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

**Announce:** "Searching marketplace for '<query>'..." (only after confirming query is non-empty)

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
