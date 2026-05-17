# Phase 12 Devlog: Status Command

## Implemented

- Added `nightshift/status.py`.
- Implemented project status inspection for config path, project root, task counts, next runnable task, latest run directory, and warnings.
- Wired `nightshift status --config ...` into the CLI.
- Added status tests.

## Decisions Made

- Status is read-only and uses existing config/task/artifact files.
- The next task is dependency-aware, so blocked tasks are not reported as runnable.
- Latest run detection is filesystem-based and uses the newest run directory by modification time.

## Notes

- Status warnings currently focus on dependency problems. Broader validation warnings can be added without changing the CLI shape.
