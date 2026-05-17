# Phase 15 Devlog: Multi-Task Run Mode

## Implemented

- Added `nightshift run --all`.
- Added `PipelineRunner.run_tasks()`.
- Processes incomplete tasks in file order.
- Reuses one artifact store/run directory for the batch.
- Stops on first failure by default.
- Added `pipeline.continue_on_task_failure` config support, defaulting to false.
- Writes aggregate run summaries with completed and failed counts.
- Added multi-task tests.

## Decisions Made

- `--all` and `--task` are mutually exclusive.
- Failed and blocked tasks count as failed in aggregate summaries.
- The default remains conservative: stop on first failure unless explicitly configured otherwise.

## Notes

- Multi-task mode is still sequential. Parallel execution remains out of scope.
