# Phase 8 Devlog: Pipeline Runner

## Implemented

- Added `nightshift/pipeline.py`.
- Executed configured stages in order for one task.
- Supported agent, agent-review, command, and summarize stages.
- Stopped on unrecoverable stage failure.
- Supported `on_fail` redirection and review-provided `next_stage` redirection.
- Tracked retry count per task.
- Enforced `pipeline.max_task_retries`.
- Wrote task snapshots, config snapshots, per-stage outputs, stage summaries, final task notes, and run summary.
- Wired `nightshift run --task TASK-001` into the CLI.
- Added tests for happy-path pipeline execution and retry-limit enforcement.

## Decisions Made

- `on_fail` takes precedence over review-provided `next_stage` because it is deterministic config controlled by the user.
- Retry count increments when a failing stage redirects to another stage. Once the configured maximum is reached, the task fails.
- The summarize stage writes a simple artifact from known stage outputs and retry notes. Rich report generation remains Phase 10.
- Pipeline execution runs one task at a time, matching the v1 constraint.

## Notes

- The runner is now sufficient for fake command-agent pipelines. Context management and fuller reports are still deferred to later phases.
