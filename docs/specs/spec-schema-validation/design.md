# Spec Schema Validation Design

## Architecture

Single-file Python script, stdlib only (`re`, `sys`, `pathlib`, `argparse`). No pip dependencies — it must run anywhere the repo is checked out, including inside a Codex sandbox.

Invocation:

```bash
python scripts/validate_specs.py docs/specs/<feature>/
```

- Argument: exactly one feature directory path
- Exit 0: valid; prints `OK: <n> delta spec(s), <m> scenario(s)`
- Exit 1: one `ERROR <relative-path>: <message>` line per violation, all violations reported (no fail-fast)
- Exit 2: usage error (missing argument, path does not exist, path is `_living`/`_archive`)

## Components

**Parser** — reads markdown structurally: `##` headings split sections (ADDED / MODIFIED / REMOVED), `###` headings inside them are behaviors, behavior bodies are scanned for GIVEN/WHEN/THEN lines and `**Was:**` / `**Now:**` / `**Reason:**` fields. Matching is case-sensitive on the keywords, tolerant of surrounding whitespace and markdown emphasis.

**Rules** (each produces zero or more errors):
1. `proposal.md` exists; its `## Intent` and `## Scope` sections are non-empty
2. `design.md` exists and is non-empty
3. `specs/` exists and contains at least one `*-delta.md`
4. Each delta file has at least one of `## ADDED`, `## MODIFIED`, `## REMOVED`
5. Each behavior under ADDED has at least one complete scenario: a GIVEN line, followed (not necessarily adjacently) by a WHEN line and a THEN line within the same behavior body
6. Each behavior under MODIFIED has `**Was:**`, `**Now:**`, `**Reason:**` and at least one complete GIVEN/WHEN/THEN scenario
7. Each behavior under REMOVED has `**Was:**` and `**Reason:**`
8. No behavior name (### heading text, case-insensitive, trimmed) appears in both MODIFIED and REMOVED across the feature's delta files

**Reporter** — collects `(path, message)` tuples, prints sorted by path then original order, sets exit code.

## Data Flow

CLI arg → resolve feature dir → run rules 1–3 on the directory → parse each delta file → run rules 4–8 → print report → exit code.

## Error Handling

- Unreadable file or undecodable bytes → single ERROR for that file, continue with others
- Empty delta file → rule 4 error, no crash
- GIVEN/WHEN/THEN may be single-line (`GIVEN x WHEN y THEN z`) or multi-line; both count as one complete scenario if all three keywords appear in order within the behavior body
- Files other than `*-delta.md` inside `specs/` (e.g., notes) are ignored
- `progress.md`, `technical-debt.md` in the feature dir are ignored

## Dependencies

None beyond Python 3.8+ stdlib. Tests use pytest with `tmp_path` fixtures building synthetic spec directories.
