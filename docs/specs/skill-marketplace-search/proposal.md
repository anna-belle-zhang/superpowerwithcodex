# Skill Marketplace Search Proposal

## Intent
Users cannot discover skills in the remote marketplace before installing. This adds a `/superpowerwithcodex:search` slash command that fetches a remote catalog and returns matching skills as detailed cards, enabling discovery before installation.

## Scope
**In scope:**
- New `commands/search.md` slash command registration
- New `skills/search-marketplace/SKILL.md` with fetch, filter, and display logic
- Case-insensitive substring matching on skill name and description
- Detailed card output per match
- Error handling for network failure, malformed catalog, missing query, no results

**Out of scope:**
- Local catalog caching
- Fuzzy or ranked matching
- Installing directly from search results
- Searching locally installed skills

## Impact
- **Users affected:** Anyone wanting to discover skills before installing
- **Systems affected:** New skill + command added; no existing files modified
- **Risk:** Low — purely additive, no existing behavior changed

## Success Criteria
- [ ] `/superpowerwithcodex:search <query> --source <url>` returns detailed cards for matching skills
- [ ] No-match query prints `No skills found for '<query>'`
- [ ] Bad URL prints a clear error message
- [ ] Malformed catalog JSON prints a clear error message
- [ ] Missing query prints usage hint
