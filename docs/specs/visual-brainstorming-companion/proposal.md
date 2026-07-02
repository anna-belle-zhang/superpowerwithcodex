# Visual Brainstorming Companion Proposal

## Intent

Bring upstream `obra/superpowers` visual brainstorming support into this fork without
losing the fork's Codex-oriented brainstorming workflow. The feature adds a local
browser companion for visual questions during brainstorming and imports the upstream
zero-dependency brainstorm server so no runtime npm dependencies are required.

## Scope

**In scope:**
- Add visual companion documentation to `skills/brainstorming/`.
- Add the companion server assets under `skills/brainstorming/scripts/`.
- Preserve this fork's deep survey step in `skills/brainstorming/SKILL.md`.
- Add a visual companion offer step before clarifying questions when visual questions are likely.
- Persist project sessions under `.superpowers/brainstorm/` when launched with `--project-dir`.
- Add focused brainstorm server tests under `tests/brainstorm-server/`.
- Ignore `.superpowers/` in `.gitignore`.

**Out of scope:**
- Full merge of upstream `skills/brainstorming/SKILL.md`.
- Removing or replacing this fork's structured specs workflow.
- Removing or replacing Codex-specific skills such as `claude-codex-specs-tdd`.
- Adding runtime npm dependencies for the server.
- Auto-opening a browser from Codex.
- Implementing new visual design assets beyond the upstream frame/helper/server files.

## Impact

- **Users affected:** Users running brainstorming in this fork who need visual mockups,
  diagrams, or layout comparisons.
- **Systems affected:** `skills/brainstorming`, `.gitignore`, and
  `tests/brainstorm-server`.
- **Risk:** Medium. The server files are additive, but the brainstorming skill text
  must be manually reconciled so upstream's visual companion gates do not remove this
  fork's deep survey and structured-spec flow.

## Success Criteria

- [ ] `skills/brainstorming/scripts/start-server.sh --project-dir "$PWD"` starts a local server and prints JSON with `url`, `screen_dir`, and `state_dir`.
- [ ] The server uses only Node.js built-ins at runtime.
- [ ] A content fragment written to `screen_dir` is served through the browser frame template.
- [ ] Browser clicks on options are recorded in `state_dir/events`.
- [ ] New HTML screens clear stale browser choice events.
- [ ] `skills/brainstorming/SKILL.md` offers the visual companion only when visual questions are likely.
- [ ] `skills/brainstorming/SKILL.md` still includes this fork's deep survey step.
- [ ] `.superpowers/` is ignored by git.
- [ ] `npm test --prefix tests/brainstorm-server` passes.
