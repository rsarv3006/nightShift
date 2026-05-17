# Phase 10 Devlog: Reports

## Implemented

- Added `nightshift/reports.py`.
- Generated final task notes.
- Generated `stage-results.md`.
- Generated run summaries.
- Included task status, retry count, final reason, acceptance criteria, stage results, artifact paths, and modified files when available.
- Wired report generation into the pipeline runner.
- Added report tests.

## Decisions Made

- Report generation is separated from the pipeline runner so formatting can evolve without changing orchestration logic.
- Modified file detection uses `git status --short` when available, but report generation succeeds if Git is unavailable or rejects the repository.
- The summarize stage remains a pipeline stage artifact; Phase 10 final reports are always generated at task completion.

## Notes

- Reports are intentionally concise markdown. They are meant to be the morning review entry point, not a full replacement for detailed artifacts.
