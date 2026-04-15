# Codex Subagent-Driven Development Workflow

- Creation date: 2026-04-06

## Overview

The codex-subagent-driven-development workflow follows a disciplined RED-GREEN-REFACTOR loop with clear ownership between Claude and Codex. Execution is sequential by default so each stage has a single source of truth. Parallel execution is used only when explicitly requested.

## RED Phase

Claude starts the workflow by writing failing tests that define the required behavior. This phase establishes the contract for the change before implementation begins.

## GREEN Phase

Codex implements the change needed to satisfy the failing tests. Implementation must stay within explicit file boundaries so the scope is controlled and review remains straightforward.

## REFACTOR Phase

Claude reviews the resulting changes and verifies that the tests now pass and that the implementation matches the intended behavior. This phase is where code quality, boundary compliance, and overall correctness are confirmed.

## Retry Chain

If the tests still fail after implementation, the workflow returns to Codex for another constrained implementation pass. If review finds issues after the tests pass, the workflow also loops back for correction, followed by another review and verification cycle.

## Execution Model

Sequential execution is the default mode for this workflow: Claude writes tests, Codex implements, and Claude reviews. Parallel work should only be introduced on explicit request, not by default.
