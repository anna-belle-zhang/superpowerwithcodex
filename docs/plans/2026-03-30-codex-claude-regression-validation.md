# Codex and Claude Code Regression Claims Validation

Date: 2026-03-30

## Purpose

Validate two related claim sets:

1. Public Codex regressions that mirror public Claude Code complaints
2. Claims made in the Substack post ["What's Going On with Claude Code?"](https://alphaguruai.substack.com/p/whats-going-on-with-claude-code), published March 23, 2026

This document distinguishes between:

- Confirmed by primary/public sources
- Partially supported
- Not validated from the sources reviewed

## Method

Primary or near-primary sources reviewed:

- GitHub issues and issue comments in `openai/codex`
- GitHub issues, issue comments, and releases in `anthropics/claude-code`
- OpenAI Developers docs for Codex `AGENTS.md`
- Anthropic docs for Claude Code
- Anthropic status history
- OpenAI Developer Community threads
- The referenced Substack article

I did not independently reproduce the model behaviors. This is a source-validation document, not a benchmark report.

## Codex Findings

### Summary

There is clear public evidence of Codex users reporting instruction-following and quality regressions. However, the stronger claims about unresolved `AGENTS.md` loading failures and silent model rerouting are not established by the source set below.

### Claim Validation

| Claim | Status | Notes | Sources |
| --- | --- | --- | --- |
| Codex does not read `AGENTS.override.md` | Partially supported, but weak as a current bug claim | [Issue #11838](https://github.com/openai/codex/issues/11838) exists and was opened on February 15, 2026, but an OpenAI collaborator explained that AGENTS content is injected by the harness without exposing paths to the model, so asking the model whether it "read" the file is unreliable. The reporter later closed the issue on March 16, 2026 after revising their understanding. Official docs now explicitly state Codex checks `AGENTS.override.md` before `AGENTS.md` along the project-root-to-cwd path. | [#11838](https://github.com/openai/codex/issues/11838), [comment](https://github.com/openai/codex/issues/11838#issuecomment-3903057246), [docs](https://developers.openai.com/codex/guides/agents-md) |
| Codex is not processing root-level `AGENTS.md` | Not validated by the cited forum post | The cited community thread exists, but its title is "Codex not processing root level Agent.md" and the accepted response points back to the documented `AGENTS.md` naming. That is not the same claim. | [Community thread 1280391](https://community.openai.com/t/codex-not-processing-root-level-agent-md/1280391), [reply](https://community.openai.com/t/codex-not-processing-root-level-agent-md/1280391/4) |
| GPT-5.3-Codex suffered severe degradation | Supported as a user-reported complaint, not as a confirmed platform change | [Issue #12446](https://github.com/openai/codex/issues/12446) exists, was opened February 21, 2026, and includes multiple corroborating user comments. An OpenAI collaborator stated they were not aware of changes to `gpt-5.3-codex` and later said no changes had been made since release, asking for `/feedback` logs instead. | [#12446](https://github.com/openai/codex/issues/12446), [comment 1](https://github.com/openai/codex/issues/12446#issuecomment-3939086297), [comment 2](https://github.com/openai/codex/issues/12446#issuecomment-3960671898) |
| GPT-5 / 5.1 / 5.2 Codex quality degraded over time | Supported as community dissatisfaction | The OpenAI Developer Community thread exists and documents user dissatisfaction. It is evidence of complaints, not root cause. | [Community thread 1366694](https://community.openai.com/t/gpt-5-5-1-and-5-2-codex-quality-degrading-over-last-month-or-so/1366694) |
| GPT-5.2 xhigh was silently routed to a lower or Codex model | Not validated; publicly disputed | [Issue #10438](https://github.com/openai/codex/issues/10438) exists, but the thread contains a plausible alternative explanation involving default `web_search` instructions affecting cutoff-date answers. An OpenAI collaborator said they investigated rerouting concerns and found no evidence of rerouting. | [#10438](https://github.com/openai/codex/issues/10438), [analysis comment](https://github.com/openai/codex/issues/10438#issuecomment-3851660864), [OpenAI reply](https://github.com/openai/codex/issues/10438#issuecomment-3851876927) |

### Codex Bottom Line

Validated:

- Public complaints about Codex quality and instruction-following regressions
- Public confusion around AGENTS behavior

Not validated:

- That current Codex docs/behavior still fail to load `AGENTS.override.md`
- That Codex silently rerouted users to a lower model

## Claude Code / Substack Findings

### Overall Assessment

The Substack article is directionally plausible in several places, especially on the existence of repeated incidents and widespread user complaints. It also overstates some claims beyond what I could validate from primary/public sources.

### Claim Validation

| Claim from article | Status | Notes | Sources |
| --- | --- | --- | --- |
| March 2026 was highly unstable for Claude infrastructure | Supported | Anthropic's status history page shows heavy incident volume in March 2026. A count from the March block on the status page yields 48 incidents listed for that month. This supports the general instability claim, even if individual incident framing in the article is somewhat selective. | [Anthropic status history](https://status.claude.com/history) |
| Anthropic had incidents around March 2-3, March 11-12, March 16-21, and March 19 auth failures / March 20 hanging behavior | Partially supported | The status page clearly shows multiple incidents across those date ranges, including login/authentication and delayed-response problems. I did not validate every exact phrase used by the article, but the general pattern is real. | [Anthropic status history](https://status.claude.com/history) |
| Claude Code users publicly reported a January 2026 quality regression beginning around January 26 | Supported | [Issue #21431](https://github.com/anthropics/claude-code/issues/21431), opened January 28, 2026, contains multiple user reports saying quality worsened beginning around January 26, 2026. | [#21431](https://github.com/anthropics/claude-code/issues/21431) |
| Anthropic confirmed a harness issue introduced January 26 and rolled back January 28 | Not validated from the sources reviewed | I found public user complaints around those dates, but I did not find a primary public Anthropic source confirming the exact "introduced Jan 26, rolled back Jan 28" harness narrative. This may exist elsewhere, but it was not validated here. | [#21431](https://github.com/anthropics/claude-code/issues/21431), [Anthropic status history](https://status.claude.com/history) |
| Thinking mode changed in Claude Code v2 and explicit `think` / `think hard` / `ultrathink` behavior became unclear | Supported | Public issue [#9072](https://github.com/anthropics/claude-code/issues/9072) documents that v2 replaced older named thinking levels with a new "Thinking On/Off" mode, while `ultrathink` remained visually special enough to confuse users. | [#9072](https://github.com/anthropics/claude-code/issues/9072), [interactive mode docs](https://docs.anthropic.com/en/docs/claude-code/interactive-mode) |
| `ultrathink` is now cosmetic and does not increase thinking depth | Not validated from primary/public docs reviewed | The article attributes this to an Anthropic engineer on Twitter/X. I did not find a primary Anthropic doc or GitHub statement confirming this exact claim. | [#9072](https://github.com/anthropics/claude-code/issues/9072) |
| Context degradation in long Claude Code sessions is real | Partially supported | This is plausible and consistent with many user complaints, and Anthropic docs make clear that Claude Code has plan/compact/session-management mechanisms for long contexts. But I did not validate the article's specific "1 in 4 retrievals fail at 1M" statistic from a primary source. | [model config docs](https://docs.anthropic.com/en/docs/claude-code/model-config), [common workflows docs](https://docs.anthropic.com/en/docs/claude-code/tutorials), [status history](https://status.claude.com/history) |
| The effective reliable context is only 200-256K | Not validated | I did not find a primary source establishing this quantitative threshold. | No primary source found |
| Claude Code team shipped many March 2026 releases while also focusing on new features | Supported | The GitHub releases feed shows 20 Claude Code releases published in March 2026, from `v2.1.66` through `v2.1.87`. Release notes include both bug fixes and new features. | [Claude Code releases](https://github.com/anthropics/claude-code/releases) |
| March priorities tilted toward growth/features rather than reliability | Inference, not a validated fact | The releases do show both feature work and reliability work. Concluding that priorities were "clearly tilted" is interpretive, not directly proven. | [Claude Code releases](https://github.com/anthropics/claude-code/releases) |

### Claude Code Bottom Line

Validated:

- March 2026 saw substantial Anthropic service instability
- There were widespread public quality complaints in late January 2026
- Claude Code shipped frequently in March 2026
- The v2 thinking-mode UX and semantics caused real public confusion

Not validated:

- The exact "Jan 26 harness bug, Jan 28 rollback" story
- The claim that `ultrathink` is merely cosmetic
- The quantitative context-window degradation claims (`1 in 4` retrieval failure, `200-256K` effective limit)
- The business-priority conclusion that Anthropic is choosing growth over reliability

## Cross-Tool Conclusion

There is enough public evidence to say that both Codex and Claude Code have had sustained user complaints about:

- degraded instruction-following
- inconsistent quality
- surprising tool/harness behavior
- weak user trust in what the agent claims it has done

What the public evidence does **not** cleanly establish is the stronger causal narrative often attached to those complaints:

- silent rerouting to lower models
- unresolved AGENTS/CLAUDE file loading failures despite current docs saying otherwise
- confirmed intentional nerfing of thinking depth

The strongest defensible statement is:

> As of March 30, 2026, public evidence supports that users of both Codex and Claude Code have experienced and reported meaningful regressions in quality and reliability, but several popular explanations for those regressions remain unproven or only partially evidenced in public sources.

## Source List

- OpenAI Codex issue #11838: https://github.com/openai/codex/issues/11838
- OpenAI Codex issue #12446: https://github.com/openai/codex/issues/12446
- OpenAI Codex issue #10438: https://github.com/openai/codex/issues/10438
- OpenAI AGENTS docs: https://developers.openai.com/codex/guides/agents-md
- OpenAI community thread 1280391: https://community.openai.com/t/codex-not-processing-root-level-agent-md/1280391
- OpenAI community thread 1366694: https://community.openai.com/t/gpt-5-5-1-and-5-2-codex-quality-degrading-over-last-month-or-so/1366694
- Substack article: https://alphaguruai.substack.com/p/whats-going-on-with-claude-code
- Anthropic status history: https://status.claude.com/history
- Anthropic Claude Code issue #21431: https://github.com/anthropics/claude-code/issues/21431
- Anthropic Claude Code issue #9072: https://github.com/anthropics/claude-code/issues/9072
- Anthropic Claude Code releases: https://github.com/anthropics/claude-code/releases
- Anthropic Claude Code interactive mode docs: https://docs.anthropic.com/en/docs/claude-code/interactive-mode
- Anthropic Claude Code tutorials/common workflows docs: https://docs.anthropic.com/en/docs/claude-code/tutorials
- Anthropic Claude Code model config docs: https://docs.anthropic.com/en/docs/claude-code/model-config
