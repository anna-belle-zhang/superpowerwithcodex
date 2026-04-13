  Specs Lifecycle (5 Skills)

  1. /superpowerwithcodex:write-specs — Author

  After brainstorming, transforms design into structured artifacts:       
  - docs/specs/<feature>/proposal.md — intent, scope, success criteria    
  - docs/specs/<feature>/design.md — technical decisions
  - docs/specs/<feature>/specs/<component>-delta.md — GIVEN/WHEN/THEN     
  scenarios (the core contract)

  Delta specs use ADDED / MODIFIED / REMOVED sections, describing only    
  what changes.

  ---
  2. spec-driven-tdd — Implement

  When Codex implements, scenarios become inviolable contracts — every    
  GIVEN/WHEN/THEN must have a passing test.

  3. claude-codex-specs-tdd — Orchestrate

  Claude writes specs, dispatches Codex with spec path, Codex implements  
  against them.

  ---
  4. /superpowerwithcodex:verify-specs — Gate before merge

  Three blocking checks:
  - Completeness — every scenario has a test
  - Correctness — each test's setup/action/assertion matches the scenario 
  - Coherence — no contradictions between deltas or against living specs  

  Also scans for // DEBT: annotations and REMOVED behaviors → writes      
  technical-debt.md.

  ---
  5. /superpowerwithcodex:archive-specs — Post-merge

  Merges deltas into docs/specs/_living/<component>.md (the rolling source   of truth), moves feature dir to
  docs/specs/_archive/YYYY-MM-DD-<feature>/.

  ---
  Directory Structure

  docs/specs/
    <feature>/specs/<component>-delta.md   ← working specs
    _living/<component>.md                 ← merged truth
    _archive/YYYY-MM-DD-<feature>/         ← history
    _technical-debt.md                     ← cross-feature debt ledger    

  Specs are optional — brainstorming offers them after design, but the    
  core workflow (brainstorm → plan → execute) works without them.


  Simple (/opsx:propose → /opsx:apply → /opsx:archive)

  Expanded (/opsx:new → /opsx:continue → /opsx:ff → /opsx:verify →        
  /opsx:sync → /opsx:bulk-archive)

  ---
  Key Differences vs superpowerwithcodex

  ┌─────────┬─────────────────────────────┬──────────────────────────┐    
  │         │          OpenSpec           │   superpowerwithcodex    │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │ Spec    │ ### Requirement + ####      │ GIVEN/WHEN/THEN          │    
  │ format  │ Scenario (WHEN/THEN)        │ scenarios                │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │         │ CLI (openspec               │                          │    
  │ Tooling │ init/update/config) + slash │ Skills only (no CLI)     │    
  │         │  commands                   │                          │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │ Living  │ openspec/specs/<capability> │ docs/specs/_living/<comp │    
  │ specs   │ /spec.md                    │ onent>.md                │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │ Archive │ openspec/changes/archive/YY │ docs/specs/_archive/YYYY │    
  │         │ YY-MM-DD-<feature>/         │ -MM-DD-<feature>/        │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │ Scope   │ Standalone product (20+ AI  │ Plugin on top of         │    
  │         │ tool support)               │ superpowers workflow     │    
  ├─────────┼─────────────────────────────┼──────────────────────────┤    
  │ Spec    │                             │ verifying-specs skill    │    
  │ verific │ /opsx:verify                │ (3-check: completeness/c │    
  │ ation   │                             │ orrectness/coherence)    │    
  └─────────┴─────────────────────────────┴──────────────────────────┘    

  Both follow the same delta-merge-archive pattern but OpenSpec is the    
  more mature, standalone product with a CLI, schema validation, and      
  broader tool support.