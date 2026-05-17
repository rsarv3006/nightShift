# Phase 11 Devlog: README

## Implemented

- Rewrote `README.md` around the implemented MVP rather than the earlier planned MVP.
- Explained what NightShift is and what it is not.
- Added development install and direct module usage.
- Added quickstart commands for `init`, `validate`, `run`, and `run --task`.
- Added task file and config examples that match the current command-backed MVP.
- Documented command-backed agent behavior and review output contracts.
- Documented the current safety model.
- Documented the artifact layout created by the runner.
- Added testing commands and a concise roadmap.

## Decisions Made

- Kept README focused on user-facing operation and reviewability instead of implementation internals.
- Described PyYAML as optional because the MVP has a small standard-library fallback parser for starter configs.
- Left future backend details in the roadmap rather than implying they already exist.

## Notes

- The README now reflects the current MVP state through Phase 10.
