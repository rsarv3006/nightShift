# MVP Devlog Summary

## Scope

The first MVP pass implemented phases 1 through 11 from `docs/vibe.md`.

## Completed Stages

- Phase 1: Python package skeleton, CLI entry point, starter project generation, and init tests.
- Phase 2: typed YAML config loading, structural validation, agent/stage reference checks, and config tests.
- Phase 3: project-root path safety, scoped path checks, artifact path safety, command allowlist checks, forbidden command fragments, and safety tests.
- Phase 4: markdown task parser, task selection helpers, useful task errors, and parser tests.
- Phase 5: artifact store, run/task directories, config and task snapshots, stage output writing, and artifact tests.
- Phase 6: command stage executor, stdout/stderr/exit code capture, output persistence, `StageResult`, and command tests.
- Phase 7: command-backed agent executor, prompt bundle construction, review output parsing, and fake-agent tests.
- Phase 8: deterministic pipeline runner, ordered stage execution, retry redirection, retry limit enforcement, CLI `run`, and pipeline tests.
- Phase 9: project/task/retry context files, agent context injection, `context-out.md`, and context tests.
- Phase 10: final task reports, stage summaries, run summaries, modified-file detection when available, and report tests.
- Phase 11: README updated to document the implemented MVP and current safety model.

## Major Decisions

- Runtime code stays dependency-light and uses the standard library where practical.
- YAML support uses PyYAML if installed, with a small fallback parser for starter configs.
- Pipelines are state machines, not DAGs.
- v1 executes one task at a time.
- Agents use the `command` backend first.
- Command stages require exact allowlist matches after whitespace normalization.
- Forbidden command fragments are checked before allowlist acceptance.
- Artifacts are markdown/text-first and are treated as product output, not debug leftovers.
- Context is compact and layered into project, task, and retry context.

## Current MVP State

NightShift can initialize a project, validate config and tasks, run a fake command-agent pipeline for one markdown task, enforce retry limits, persist artifacts, and produce reviewable summaries.

## Remaining Product Gaps

- Real local model backends are not implemented.
- `nightshift status` remains a placeholder.
- Clean-worktree enforcement is configured but not fully implemented.
- Diff patch capture is not implemented.
- Task completion mutation is not implemented.
- Dependency solving is not implemented.
- Multi-task overnight batching is not implemented.
