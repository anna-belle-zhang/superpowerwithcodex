The bigger problem: Claude 4.6 + Claude Code regression (~March 16-17)  

  This is the real reason skills that "worked before" now don't:

  #36093 — Severe instruction adherence regression since ~March 16-17,    
  correlated with server-side changes after the 1M context GA. Users with 
  structured skills report:
  ▎ "The model reads skills, can recite them, but does not follow them."  
  ▎ "Feels like a 6-month rollback. Skills ignored, shallow reasoning,    
  trial-and-error instead of structured analysis."

  #40489 — Opus 4.6 ignores hooks, CLAUDE.md, and startup sequences.      
  Specifically mentions superpowers using-superpowers skill conflicting   
  with custom startup sequences. Claude acknowledges the instructions are 
  in context but doesn't follow them.

  Bottom line: The finishing-a-development-branch skill not working as    
  before is likely a combination of:
  1. Pre-existing bugs in the skill itself (#999, #940)
  2. The broader Claude 4.6 instruction-adherence regression (#36093)     
  where the model reads skill instructions but doesn't reliably follow    
  them

  The regression appears to be server-side (not a Claude Code version     
  issue), which means there's no local workaround — it's affecting all    
  Max/Opus users with structured skills since mid-March.

    Claude 4.6 instruction-adherence regression: No fix in obra/superpowers 

  obra/superpowers has no open PRs or issues specifically addressing the  
  Claude 4.6 regression (~March 16-17). The community there hasn't filed  
  anything about it. The regression is server-side at Anthropic — it's not   something a skills repo can fully fix.

  What you can do in your fork

  Since those upstream PRs are ready but stuck, you could cherry-pick     
  their fixes now. Want me to pull in the fixes from PR #391, #913, and   
  #952 into your fork's finishing-a-development-branch skill?


    The regression is NOT model-specific

  Switching from Opus 4.6 to Sonnet 4.5 doesn't fix it. Multiple issues   
  confirm this:

  #36093 states the hypothesis directly: the regression is server-side    
  inference changes deployed ~March 16-17, correlated with the 1M context 
  GA going fully live. Since it's infrastructure-level, it affects all    
  models routed through the same backend.

  #31480 documents the same pattern: "output quality consistent with      
  Sonnet 3.5, not Opus 4.6" — suggesting models are being silently        
  downgraded or routed differently server-side.

  #28469 (15 comments, heavy upvotes) confirms: before Opus 4.5 in early  
  January, everything worked. After the 1M GA rollout, all models
  degraded. Users describe:
  - Model reads skills/CLAUDE.md correctly, can recite them, but doesn't  
  follow them
  - "Reading for context vs. reading for instructions" — treats skill     
  files as background info rather than imperatives
  - Instructions ignored on the very next turn after being read

  Root cause (community consensus)

  Not a bug in 4.6 specifically. It's a server-side inference optimization   Anthropic deployed to handle the load from the 1M context GA promotion.   The optimization appears to have reduced instruction-following fidelity   across all model variants.

  The only known mitigation (from issue comments)

  One commenter found the only reliable workaround — enforce critical     
  rules via hooks instead of CLAUDE.md/skills:

  # UserPromptSubmit hook — re-injects rules every single turn
  jq -n --arg r "ENFORCED RULES: [your critical rules here]" \
    '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additional  Context":$r}}'

  ▎ "When model quality regresses, CLAUDE.md instructions are the first   
  casualty because they depend on the model's instruction-following       
  ability. Hooks don't — they execute at the process level regardless of  
  model behavior."

  This is likely why the finishing-a-development-branch skill stops       
  working — it depends on multi-step instruction following that the model 
  now skips. The fix embedded in our command files helps slightly (content   is right there, no Skill tool needed), but the underlying regression   
  means the model may still not fully comply.

    No — recent Claude Code releases did NOT fix this

  Going through v2.1.81 → v2.1.87 (all releases since the regression), not   a single one mentions:
  - Instruction adherence fixes
  - Skill following improvements
  - CLAUDE.md compliance
  - Model behavior corrections

  The releases are all infrastructure: UI fixes, MCP improvements,        
  performance, worktree bugs.

  Why Claude Code can't fix it

  The regression is server-side at the model level, not in the Claude Code   client. Claude Code releases can't fix it — only Anthropic changing how   they serve the model can. And there's no public acknowledgment from    
  Anthropic staff anywhere in these issues.

  The core problem

  ┌─────────────────────────────────────┬─────────────────────────────┐   
  │          What users report          │     Anthropic response      │   
  ├─────────────────────────────────────┼─────────────────────────────┤   
  │ Skills loaded, recited back         │ No staff comments on any    │   
  │ correctly, then ignored             │ major regression issue      │   
  ├─────────────────────────────────────┼─────────────────────────────┤   
  │ Regression since ~March 16-17,      │ Bot auto-closes issues as   │   
  │ affects ALL models (not just 4.6)   │ "stale"                     │   
  ├─────────────────────────────────────┼─────────────────────────────┤   
  │ Switching to 4.5 has same problem   │ Issues closed as duplicates │   
  │                                     │  of each other              │   
  ├─────────────────────────────────────┼─────────────────────────────┤   
  │ #18660 closed as "stale" — same     │ Same pattern repeating      │   
  │ issue still open as #36093          │                             │   
  └─────────────────────────────────────┴─────────────────────────────┘   

  Workaround teams are using

  The only mitigation that actually works (from the community):

  Re-inject critical rules via UserPromptSubmit hook every single turn —  
  not just at session start:

  # hooks/enforce-rules.sh — fires before EVERY user message
  jq -n --arg rules "MANDATORY: [your critical rules]" \
    '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additional  Context":$rules}}'

  This bypasses the model's instruction-following failure because hooks   
  run at the process level regardless of model behavior. It's why we also 
  embedded skill content directly in command files — reducing how much the   model has to "remember to follow" vs. having it right in front of it   
  every time.

  Bottom line: Until Anthropic acknowledges and fixes the server-side     
  regression, teams are working around a broken model, not a broken tool. 

    Root cause the community found

  From https://alphaguruai.substack.com/p/whats-going-on-with-claude-code:
  ▎ When Claude Code v2.0.x shipped with thinking mode enabled by default,   an Anthropic engineer confirmed the explicit triggers are now cosmetic 
  and don't increase thinking depth — resulting in Claude skipping deep   
  analysis and jumping straight to action.

  This explains why skills get read but not followed — the model isn't    
  spending tokens reasoning through multi-step processes anymore.

  The internet's consensus on fixing it

  From https://jessezam.medium.com/hooks-rules-and-skills-feedback-loops-i  n-claude-code-d47e5f58364d and https://www.shareuhack.com/en/posts/claud  e-code-claude-md-setup-guide-2026:

  ▎ "If CLAUDE.md and skills are about guidance, hooks are about 
  guarantees."
  ▎ Rules should not be used to enforce behavior that needs to be         
  absolute. Hooks are mechanically executed and don't depend on LLM       
  judgment.


 I analyzed clauderegression.md and ran a subagent that verified every claim against
  livecsources.tThenheadline:athe note's facts all check out, but it's now badly outdated — 
  Anthropic published an official post-mortem on April 23, 2026 acknowledging and fixing the 
  regression, with a different root cause than the note hypothesized.o select · Enter to view
  What the note got right

  - Every GitHub reference is genuine — nothing fabricated. Issues #36093  (https://github.com/anthropics/claude-code/issues/36093), #40489
  (https://github.com/anthropics/claude-code/issues/40489), #31480  (https://github.com/anthropics/claude-code/issues/31480), #28469
  (https://github.com/anthropics/claude-code/issues/28469), #18660
  (https://github.com/anthropics/claude-code/issues/18660) all exist with the described
  content, and zero Anthropic staff ever commented on any of them (all closures were by the
  stale bot).
  - The regression itself was real. Users complaining in the March window were vindicated.
  - The hooks workaround is sound. The "hooks are guarantees, CLAUDE.md is guidance"
  principle is genuine community consensus, and the UserPromptSubmit re-injection trick was  indeed posted on #36093/#40489. (This repo's own hooks/hooks.json already implements it.)
  - All three cited blog posts exist and say roughly what the note claims. The 1M-context GA  is real and correctly dated (March 13, 2026).

  What's now stale or contradicted
  1. "Server-side inference optimization, no acknowledgment, no fix" — superseded.  Anthropic's April 23 post-mortem
  (https://www.anthropic.com/engineering/april-23-postmortem) attributed everything to three  client/harness-layer changes, and explicitly cleared the inference layer:
    - March 4: default reasoning effort silently dropped from high to medium — reverted April
  7    - March 26: caching bug cleared thinking/session state every turn — fixed April 10 in
  v2.1.101    - April 16: anti-verbosity system-prompt change hurt coding quality — reverted April 20
  in v2.1.116

  They also reset subscriber usage limits as a goodwill gesture. So the note's central  "server-side, tied to 1M GA" hypothesis was contradicted, and the "silently swapped to 4.5"
  theory in #31480 remains pure speculation.  2. The upstream superpowers fixes are no longer "stuck." obra/superpowers issues #999/#940
  were closed as completed on April 27 — the finishing-a-development-branch skill got a full  detect-and-defer rewrite via PR #1121, shipped in superpowers v5.1.0 (May 4). PRs
  #391/#913/#952 were closed unmerged as superseded. Cherry-picking them, as the note  suggests, would now be the wrong move — pulling the v5.1.0 rewrite from upstream is the
  right one.
  3. The "thinking triggers are cosmetic" claim is dated — ultrathink was restored in Claude
  Code v2.1.68 (maps to high effort for the turn).  4. One nuance worth keeping: #18660 and #28469 predate the March regression, so "skills
  read but not followed" is really two layered problems — a chronic LLM instruction-adherence  limitation (still true, hooks still the right mitigation) underneath an acute regression
  that has since been fixed.

  Bottom line

  The note was accurate journalism for late March but its conclusions ("no fix possible, no  acknowledgment, work around a broken model") no longer hold. The acute regression is fixed
  (be on Claude Code ≥ v2.1.116; current is v2.1.173), the upstream skill bugs are fixed in
  superpowers v5.1.0, and the durable takeaway that survives is the architecture lesson:
  enforce critical rules via hooks, advisory guidance via CLAUDE.md/skills — which this fork
  already does.

  If you want, I can update clauderegression.md with a dated addendum reflecting all of this,  and/or look at syncing the upstream v5.1.0 finishing-a-development-branch rewrite into
  this fork.