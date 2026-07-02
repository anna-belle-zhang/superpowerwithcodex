---
name: brainstormlight
description: Use when refining a rough idea and the user is busy, wants rapid-fire questioning, or says "just ask me questions" - grill-me style interrogation with exactly one question per message, each carrying a recommended answer dug from the codebase, every confirmed decision written immediately to a ledger file so Claude Code or Codex can resume the session if the other degrades or crashes
---

# Brainstorm Light (Grill Me)

## Overview

Lightweight alternative to full brainstorming: you interrogate the user one
question at a time, each question carrying your recommended answer, and you
write every confirmed decision to a ledger file the moment it is confirmed.
The user only confirms or redirects — minimal cognitive load. The ledger makes
the session portable: any agent (Claude Code or Codex) can pick it up mid-way.

**Core principle: the chat is disposable; the ledger is the session.**
A decision that exists only in chat does not exist.

## When to Use

- User is busy, answering in small slices, or hates long documents
- User asks for "grill me" / rapid questions / lightweight refinement
- Session may be handed between Claude Code and Codex

Use full `superpowerwithcodex:brainstorming` instead when the user wants
alternatives explored in depth or a sectioned design document.

## The Loop

**0. Re-entry check:** Look for an existing ledger at
`docs/plans/YYYY-MM-DD-<topic>-grill.md`. If found, read it, tell the user
what is already settled, and resume from Open Questions. Never re-ask a
settled decision.

**1. Create the ledger FIRST** — before asking your first question, create
`docs/plans/YYYY-MM-DD-<topic>-grill.md`:

```markdown
# <Topic> — Decision Ledger
Status: in progress
## Decisions
(none yet)
## Open Questions
- <everything you currently don't know, one line each>
```

**2. Dig before you ask.** Explore the codebase. Any open question the code
already answers (naming conventions, existing config patterns, prior art):
record it as a decision with source `codebase`, delete it from Open
Questions, and move on without asking.

**3. Ask ONE question per message.** Exactly one. Not "two quick questions",
not "pick one to answer first". Format:

> **Q:** Where should the timeout be configured?
> **My recommendation:** env var `COMPANION_SESSION_TTL`, because the server
> already reads `COMPANION_*` vars in server.cjs. OK?

Every question MUST carry a recommendation with a one-line reason. The user
should be able to answer with one word.

**4. Record IMMEDIATELY.** The moment the user answers, append the decision
to the ledger and remove the open question — before sending your next
message. Not at the end. Not when a handoff is announced. Every turn.

Decision line format:
`N. <decision> — (user | codebase | recommended+confirmed)`

**5. Finish.** When Open Questions is empty, set `Status: complete`, reply
with the decision list only (no design document), and offer
`superpowerwithcodex:write-specs`.

**Batch exception:** Only if the user explicitly asks for all questions at
once, send at most 5, each with a recommendation, and say "reply 'all OK' or
list exceptions."

## Rationalizations — All Wrong

| Excuse | Reality |
|--------|---------|
| "I'll write to disk at the very end, after the user approves" | Crash mid-way loses every decision. Ledger from turn one. |
| "Two quick questions is basically one" | Two is two. One question per message. |
| "The user is busy, I'll batch to save their time" | Batching raises their load. One confirmable question is faster to answer. |
| "This question is too open-ended for a recommendation" | Then you haven't dug enough. Read the code, pick a default, recommend it. |
| "I'll summarize decisions when a handoff is announced" | Crashes don't announce themselves. Persist per-turn. |
| "Updating the file every turn is wasteful" | One append per turn is trivial. Lost sessions are not. |

## Red Flags — STOP

- A message containing two question marks aimed at the user
- A question without "My recommendation:"
- Any confirmed decision not yet in the ledger when you send your next message
- Presenting a multi-section design document
- "I'll write the file once we're done"
