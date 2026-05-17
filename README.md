# NightShift

> Auditable local-first AI coding pipelines.
>
> Wake up to reviewable work, not chaos.

NightShift is a deterministic pipeline runner for long-running AI-assisted coding workflows.

It is designed for overnight or unattended execution against a scoped project repository using local or external coding agents.

NightShift is not an autonomous coding god.

It is a safety-aware orchestration system that treats LLMs like unreliable distributed systems.

Agents are bounded by:

* scoped repository access
* structured pipeline stages
* tests and static analysis
* retry limits
* review stages
* context compaction
* durable artifacts

The output is:

* reviewable code
* plans
* logs
* diffs
* test output
* review notes
* overnight summaries

Not blind autonomous shipping.

---

# Why?

Most "AI coding agents" optimize for:

* autonomy
* demo magic
* speed
* vibes

NightShift optimizes for:

1. Cheapness
2. Correctness
3. Auditability
4. Speed

NightShift is also intended to serve as an experimentation platform for AI-assisted software engineering workflows.

The system is intentionally designed to facilitate testing and comparison of:

* different models
* different agent roles
* prompt structures
* system prompts
* retry strategies
* review strategies
* context compaction techniques
* pipeline structures
* reasoning formats
* constraint-driven workflows

The pipeline architecture should make these experiments reproducible, auditable, and configurable rather than hidden inside opaque agent behavior.

The assumption is simple:

> AI systems are useful but unreliable.

NightShift embraces this reality by building deterministic orchestration around nondeterministic agents.

---

# Features

## Local-first execution

Designed primarily for:

* Ollama
* local models
* Codex CLI
* Claude Code
* command-driven wrappers

Use cheap local models for most work.
Escalate expensive models only where useful.

---

## Declarative pipelines

Define workflows in YAML:

```yaml
pipeline:
  stages:
    - id: plan
      type: agent
      agent: planner

    - id: implement
      type: agent
      agent: implementer

    - id: test
      type: command
      commands:
        - cargo test

    - id: review
      type: review
      agent: reviewer
```

Pipelines are intentionally portable and configurable so users can experiment with:

* model routing
* review loops
* retry logic
* prompt engineering
* reasoning formats
* planning strategies
* context structures
* cost/performance tradeoffs

NightShift is designed to make these workflow experiments measurable and repeatable rather than ad-hoc.

```yaml
pipeline:
  stages:
    - id: plan
      type: agent
      agent: planner

    - id: implement
      type: agent
      agent: implementer

    - id: test
      type: command
      commands:
        - cargo test

    - id: review
      type: review
      agent: reviewer
```

---

## Review-first workflows

NightShift is designed around:

```text
plan
  -> review
  -> implement
  -> test
  -> static analysis
  -> review
  -> retry or complete
```

The goal is:

> Wake up to a useful review package.

---

## Durable artifacts

Every run creates a full audit trail.

Example:

```text
.nightshift/
  runs/
    2026-05-16-overnight/
      run-summary.md

      tasks/
        TASK-001/
          plan.md
          review.md
          implementation-log.md
          test-output.txt
          diff.patch
```

This makes:

* debugging easier
* prompt experimentation possible
* retries understandable
* failures inspectable
* portfolio demos stronger

---

## Scoped repository safety

NightShift can:

* restrict writable directories
* allowlist commands
* block dangerous shell operations
* require clean git worktrees

The system is intentionally conservative.

---

# Philosophy

NightShift follows a few core principles.

## Deterministic orchestration

Agents are probabilistic.

The pipeline runner should not be.

---

## Context compaction

Do not dump infinite history into prompts.

Use:

* project context
* task context
* retry summaries

Keep context compact and intentional.

---

## Reviewability over autonomy

NightShift is optimized to produce:

* reviewable work
* reviewable reasoning
* reviewable failure

Not autonomous deployment.

---

## Boring reliability beats magical demos

The system should:

* fail clearly
* retry explicitly
* preserve artifacts
* avoid spooky hidden behavior

---

# Architecture Overview

```text
Task Parser
    ↓
Pipeline Runner
    ↓
Stage Executor
 ┌────┴────┐
 ↓         ↓
Agents   Commands
```

Core components:

* Task parser
* Pipeline runner
* Stage executor
* Agent wrappers
* Command runner
* Artifact store
* Context manager
* Safety layer

---

# Example Workflow

Input:

* repository
* tasks.md
* nightshift.yaml
* agent prompt files

Execution:

```text
TASK-001
  ↓
plan
  ↓
review_plan
  ↓
implement
  ↓
test
  ↓
static analysis
  ↓
review
  ↓
complete or retry
```

Output:

* modified repository
* task artifacts
* overnight report
* review notes

---

# Installation

## Status

NightShift is currently an early-stage project.

The MVP focuses on:

* local-first execution
* declarative pipelines
* task orchestration
* artifact generation
* safe command execution
* reviewable workflows

---

## Planned Installation

Python version:

```bash
pip install nightshift
```

Development install:

```bash
git clone <repo>
cd nightshift
pip install -e .
```

---

# Quickstart

## 1. Initialize a project

```bash
nightshift init
```

Creates:

```text
nightshift.yaml
tasks.md
agents/
```

---

## 2. Define tasks

Example:

```markdown
- [ ] TASK-001: Add YAML config loading

Description:
Implement config loading for NightShift.

Acceptance Criteria:
- Loads `nightshift.yaml`
- Validates required fields
- Includes tests
```

---

## 3. Configure pipeline

Example:

```yaml
project:
  root: .
  task_file: tasks.md
  artifact_dir: .nightshift

pipeline:
  max_task_retries: 3
```

---

## 4. Run NightShift

```bash
nightshift run
```

Or:

```bash
nightshift run --task TASK-001
```

---

## 5. Review artifacts

```text
.nightshift/runs/<run-id>/
```

Contains:

* plans
* logs
* diffs
* test output
* review notes
* summaries

---

# Example Config

```yaml
project:
  name: example-project
  root: .
  task_file: tasks.md
  artifact_dir: .nightshift

safety:
  require_clean_worktree: true

  scoped_paths:
    - src/
    - tests/

  allowed_commands:
    - cargo test
    - cargo fmt --check

  forbidden_commands:
    - rm -rf
    - git push

agents:
  planner:
    backend: command
    command: codex
    system_prompt: agents/planner.md

  implementer:
    backend: command
    command: codex
    system_prompt: agents/implementer.md

  reviewer:
    backend: command
    command: codex
    system_prompt: agents/reviewer.md

pipeline:
  max_task_retries: 3

  stages:
    - id: plan
      type: agent
      agent: planner

    - id: implement
      type: agent
      agent: implementer

    - id: test
      type: command
      commands:
        - cargo test

    - id: review
      type: review
      agent: reviewer
```

---

# Safety Model

NightShift intentionally limits agent freedom.

## Repository scope restrictions

Agents should only operate within configured project paths.

---

## Command allowlists

Commands must be explicitly permitted.

Example:

```yaml
allowed_commands:
  - cargo test
  - cargo fmt --check
```

---

## Dangerous command blocking

NightShift may block commands such as:

```text
rm -rf
git push
curl | bash
```

---

## Review-first workflow

The system assumes:

> Humans remain the final authority.

---

# Roadmap

## MVP

* [ ] YAML config loading
* [ ] Markdown task parsing
* [ ] Pipeline execution
* [ ] Fake command agents
* [ ] Artifact generation
* [ ] Safe command execution
* [ ] Retry handling
* [ ] Overnight reports

## Future

* [ ] Ollama integration
* [ ] Claude Code integration
* [ ] Codex integration
* [ ] Parallel execution
* [ ] DAG workflows
* [ ] Prompt A/B testing
* [ ] Cost telemetry
* [ ] Git branch isolation
* [ ] Dashboard UI
* [ ] Constraint-language experimentation

---

# Inspiration

NightShift is inspired by:

* CI/CD systems
* build pipelines
* state machines
* agent orchestration research
* distributed systems thinking
* local-first tooling
* practical AI skepticism

---

# Philosophy Statement

NightShift rejects two extremes:

## Fully manual engineering

Too slow.

## Reckless autonomous agents

Too unreliable.

Instead:

> NightShift treats AI systems as bounded workers inside deterministic workflows.

The goal is not artificial software gods.

The goal is trustworthy leverage.

---

# License

Planned:

GPLv3

Rationale:

NightShift is licensed under GPLv3 because AI-assisted software engineering is rapidly becoming dependent on opaque, vendor-controlled tooling. As agent systems become part of the actual software production process, users deserve the freedom to inspect, modify, audit, and reproduce the systems operating on their codebases. GPLv3 helps ensure that improvements to NightShift and its orchestration layer remain part of a transparent, inspectable ecosystem rather than disappearing into proprietary black boxes. The goal is not just open source for its own sake, but preserving user autonomy, local-first experimentation, and the ability to understand how automated systems are making decisions inside increasingly critical engineering workflows.

* encourages community contribution
* protects local-first ecosystem
* aligns with hacker/free software ethos

[Read more here, GPLv3 saves the world.](https://www.gnu.org/licenses/rms-why-gplv3.html)

---

# Contributing

NightShift is intentionally early and experimental.

Good contributions:

* safety improvements
* pipeline reliability
* better artifact systems
* better context compaction
* local model integrations
* tests
* docs

Bad contributions:

* adding magical autonomy before reliability exists
* removing safety boundaries
* overcomplicated abstractions before MVP stability

---

# Final Note

AI coding tools are currently optimized for demos.

NightShift is optimized for surviving the night.
