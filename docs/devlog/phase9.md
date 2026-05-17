# Phase 9 Devlog: Context Manager

## Implemented

- Added `nightshift/context.py`.
- Created project context files when absent.
- Created per-task `context.md` files.
- Added compact task context with task id, title, description, and acceptance criteria.
- Passed project context, task context, and retry context into agent prompt bundles.
- Persisted `context-out.md` after task execution.
- Included review `context_update` values in retry/context output notes.
- Added context manager tests and prompt coverage for task/retry context.

## Decisions Made

- Context files are plain markdown artifacts so they remain readable and easy to edit.
- Retry context is built from compact retry notes rather than full previous transcripts.
- Durable project-context bubbling is implemented as an explicit helper, but the pipeline does not automatically append every task detail into project context.

## Notes

- Later phases can decide which completed-task facts are worth promoting into project context.
