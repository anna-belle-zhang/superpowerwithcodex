# Brainstorming Skill Delta Spec

## MODIFIED

### Visual companion offer added to brainstorming flow
**Was:** The brainstorming skill moved from project context exploration directly into clarifying questions.
**Now:** After project context exploration, the skill offers the visual companion when upcoming questions are likely to benefit from visual mockups, diagrams, or layout comparisons.
**Reason:** Visual questions are easier to answer when users can inspect and select options in a browser.

GIVEN the brainstorming skill is loaded
AND the user's request is likely to involve visual choices
WHEN the agent finishes initial project context exploration
THEN the agent offers the visual companion before asking detailed clarifying questions
AND the offer is sent as its own message with no additional question or context summary

### Text-only brainstorming preserved when companion is not useful
**Was:** All brainstorming happened in terminal text.
**Now:** Terminal text remains the default unless a specific upcoming question would be clearer visually.
**Reason:** Browser screens should be an optional tool, not a mandatory mode.

GIVEN the brainstorming skill is loaded
AND the next question is about requirements, scope, technical tradeoffs, or conceptual choices
WHEN the agent decides how to ask the question
THEN the agent asks in the terminal
AND does not start or use the visual companion for that question

### Companion consent controls server use
**Was:** There was no browser companion server.
**Now:** The agent starts or uses the companion only after the user accepts the standalone offer.
**Reason:** The companion requires opening a local URL and may add token and workflow overhead.

GIVEN the agent has offered the visual companion
WHEN the user declines
THEN the agent continues text-only brainstorming
AND does not start the brainstorm server

GIVEN the agent has offered the visual companion
WHEN the user accepts
THEN the agent may start the brainstorm server
AND may use browser screens for later visual questions

### Deep survey step remains in place
**Was:** This fork's brainstorming skill performed a deep survey after understanding the purpose.
**Now:** The deep survey still happens after purpose is understood and before approach selection, even when the visual companion has been accepted.
**Reason:** The fork's Codex-oriented workflow depends on local and external context before proposing designs.

GIVEN the brainstorming skill is loaded from this fork
AND the user's purpose is understood
WHEN the agent prepares to propose approaches
THEN the agent performs the existing deep survey step
AND uses the survey results to anchor the proposed approaches

### Visual companion guide is loaded only after acceptance
**Was:** No visual companion guide existed.
**Now:** If the user accepts the companion, the agent reads `skills/brainstorming/visual-companion.md` before using browser screens.
**Reason:** The guide contains operational details for server lifecycle, file naming, event handling, and cleanup.

GIVEN the user accepts the visual companion
WHEN the agent prepares to start or use the companion
THEN the agent reads `skills/brainstorming/visual-companion.md`
AND follows its operating loop for visual questions

## ADDED

### Stale browser content is cleared when returning to terminal
GIVEN the visual companion has shown a browser screen
AND the next brainstorming step does not need a visual
WHEN the agent returns to terminal-only discussion
THEN the agent writes a waiting screen to the session content directory
AND tells the user the conversation is continuing in the terminal
