## Spec Fingerprint

Mode: FULL
Combined sha256: b7dd01fdc7ff12b7823e615bd226ae8ab850ee63c0cdbcc032b21e9402396c63

- b0f9ccf86bb3ed2bc59e1c4ee907730e0c89ac6e1c6bf5c558d6078b4f9409a6  proposal.md
- 9da3c21fe6005ece766c876ad27df8a9db8b4c480f3f12e4e18e5eb86236daa4  design.md
- b721a3596b86dd6d834f84c97a5d3232c6fa7eeb4e2e36cb4cd944f8af2426bd  specs/handover-manager-delta.md
- 0fe1887aa00a14e64193bb1192789585dd3d9efcbebefecadc178dae410a6cf3  specs/learn-delta.md
- 3855c4451479012fa0097b6c0f0fc09378a647f857423bcf1adb9b53823e104e  specs/lessons-format-delta.md

## Plan

- [x] Task 1: lessons validator CLI and missing-file success
- [x] Task 2: lessons entry shape, required fields, heading/tag, level, duplicate tag, promotion, and occurrence validation
- [x] Task 3: learn skill conventions and deterministic behavior text coverage
- [x] Task 4: handover-manager wrap-up chains into learn scan without changing handover content
- [x] Task 5: full structured-specs integration verification

## Issues

(empty)

## Verification

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/structured-specs-integration/test_validate_lessons.py tests/structured-specs-integration/test_learn_skill.py -q` -> 19 passed in 1.27s
- `python -m pytest tests/structured-specs-integration/ -q` -> 253 passed in 7.26s

## Commits

(empty)
