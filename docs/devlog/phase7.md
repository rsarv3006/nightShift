# Phase 7 Devlog: Agent Executor

## Implemented

- Added `nightshift/agents.py`.
- Implemented the v1 `command` backend for agents.
- Loaded system prompt files through project-root-safe path resolution.
- Built compact prompt bundles containing system prompt, task markdown, acceptance criteria, project context, previous stage output, retry notes, and output contract.
- Passed prompt bundles to command agents on stdin.
- Captured stdout, stderr, exit code, duration, and timeout state.
- Persisted agent output and prompt artifacts through the artifact store.
- Parsed structured review-agent output into `StageResult`.
- Added fake-agent tests.

## Decisions Made

- Agent commands are command strings and run with `shell=True`, matching the Phase 6 command-string model. Unlike validation/test commands, agent commands are configured agent backends rather than allowlisted project commands.
- Agent stages pass when the command exits successfully. Review stages must emit a valid `status:` field or they fail.
- Prompt artifacts include the exact prompt sent to the agent to support auditability and prompt debugging.

## Notes

- Only the `command` backend is implemented. Ollama, Codex CLI, Claude Code, and API backends remain future integrations.
