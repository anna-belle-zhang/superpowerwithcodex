---
name: brainstorming
description: Use when creating or developing, before writing code or implementation plans - refines rough ideas into fully-formed designs through collaborative questioning, alternative exploration, and incremental validation. Don't use during clear 'mechanical' processes
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- If upcoming questions will involve visual content, offer the visual companion once before asking detailed clarifying questions. The offer must be its own message. See the Visual Companion section below.
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Deep survey (after understanding purpose):**
- Default to a Codex subagent for the survey unless another agent is explicitly better suited
- Dispatch the survey directly — research is read-only and low-risk; don't ask permission first
- Have the subagent gather both local and external context relevant to the stated purpose: existing types/schemas, API endpoints, client integrations, recent commits touching this domain, and internet research for standards, vendor docs, libraries, or prior art that materially affect the design
- Tell the subagent to separate confirmed facts from inferences and to cite the external sources it used
- Use the survey report to anchor the design — don't propose approaches until you know what already exists locally and what external constraints or options matter

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Structured Specifications (recommended):**
- Ask: "Would you like structured specs with testable scenarios?"
- If yes: Use `superpowers:write-specs` to create proposal + delta specs with GIVEN/WHEN/THEN scenarios
- If no: Keep design doc in `docs/plans/` (legacy format) and proceed to implementation

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create detailed implementation plan

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense

## Visual Companion

A browser-based companion can show mockups, diagrams, and visual options during
brainstorming. It is a tool for visual questions, not a mode for the whole session.

**Offering the companion:** When upcoming questions will involve visual content
(mockups, layouts, diagrams, or side-by-side visual comparisons), offer it once:

> Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)

This offer must be its own message. Do not combine it with clarifying questions,
context summaries, or any other content. Wait for the user's response before
continuing. If they decline, proceed with text-only brainstorming.

**Per-question decision:** Even after the user accepts, decide for each question
whether to use the browser or the terminal. Use the browser when seeing the
content is clearer than reading it: UI mockups, architecture diagrams,
side-by-side layouts, visual hierarchy, or spatial relationships. Use the
terminal for requirements, scope, conceptual choices, tradeoffs, and technical
decisions.

If they accept the companion, read `skills/brainstorming/visual-companion.md`
before using browser screens. Follow its server lifecycle, file naming, event
reading, and stale-screen cleanup guidance.
