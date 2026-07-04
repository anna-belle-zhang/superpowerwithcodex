# handover-manager Delta Spec

`skills/handover-manager/SKILL.md` — wrap-up chains into the learn scan.

## MODIFIED

### Wrap-Up Invokes the Learn Scan
**Was:** handover generation ends after docs/handovers/LATEST.md is updated
**Now:** after LATEST.md is updated, the wrap-up invokes the learn skill's passive scan as its final step
**Reason:** the flow-layer design makes learn's passive trigger part of session wrap-up; without chaining, lessons are only captured when the user remembers to ask

GIVEN a handover has been generated and LATEST.md updated
WHEN the wrap-up completes
THEN the learn scan runs and presents its candidate list (or reports no candidates) before the session is considered wrapped up

### Handover Content Unaffected by Scan Outcome
**Was:** handover document content defined by the six-section format
**Now:** identical — the learn scan runs after the handover is written and never modifies it
**Reason:** the handover is a verified snapshot; lesson capture must not retroactively edit it

GIVEN the learn scan produces candidates or errors after a handover is written
WHEN the wrap-up finishes
THEN the handover document and LATEST.md remain exactly as generated
