# Finishing A Development Branch Delta Spec

## MODIFIED

### Branch Wrap-Up Sequence
**Was:** Verify tests (and specs if they exist), then present merge/PR/cleanup options
**Now:** Verify tests (and specs if they exist), write a handover via handover-manager, then present merge/PR/cleanup options
**Reason:** Branch completion is a session boundary; a handover makes the finished state resumable from any tool without relying on chat history

GIVEN a development branch where implementation is complete and tests pass
WHEN the finishing-a-development-branch skill runs
THEN a handover document is generated before merge/PR options are presented, and its status field is set to done
