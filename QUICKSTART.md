# NightShift Quickstart

This guide runs the current MVP with safe example files.

## 1. Install for Development

```bash
pip install -e .
```

Or run the module directly:

```bash
python -m nightshift.cli --help
```

## 2. Create Starter Files

From a project directory:

```bash
nightshift init
```

This creates:

```text
nightshift.yaml
tasks.md
agents/
```

Existing starter files are not overwritten unless you pass `--force`.

## 3. Validate

```bash
nightshift validate
```

Validation checks config structure, task parsing, prompt files, scoped paths, and command safety.

## 4. Run One Task

Run the next incomplete task:

```bash
nightshift run
```

Run a specific task:

```bash
nightshift run --task TASK-001
```

## 5. Review Artifacts

After a run, inspect:

```text
.nightshift/runs/<run-id>/
```

Useful files:

```text
run-summary.md
config.snapshot.yaml
tasks/TASK-001/task.md
tasks/TASK-001/context.md
tasks/TASK-001/plan.md
tasks/TASK-001/test-output.txt
tasks/TASK-001/stage-results.md
tasks/TASK-001/context-out.md
tasks/TASK-001/final-notes.md
```

## Example Templates

Example run files are available in `templates/`.
They are safe starter examples and use command-backed fake agents.
