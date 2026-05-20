"""Post-run explanation reports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .errors import NightShiftError
from .status import latest_run_dir


@dataclass(frozen=True)
class WhatHappenedReport:
    run_dir: Path
    task_dir: Path | None
    content: str


def build_what_happened(
    project_root: str | Path,
    artifact_dir: str | Path,
    *,
    run_id: str = "latest",
    task_id: str | None = None,
) -> WhatHappenedReport:
    root = Path(project_root).resolve()
    artifacts = (root / artifact_dir).resolve()
    runs_dir = artifacts / "runs"
    run_dir = _select_run_dir(runs_dir, run_id)
    task_dir = _select_task_dir(run_dir, task_id)
    content = format_what_happened(run_dir, task_dir)
    return WhatHappenedReport(run_dir=run_dir, task_dir=task_dir, content=content)


def format_what_happened(run_dir: Path, task_dir: Path | None) -> str:
    lines = ["# What Happened", "", f"Run: `{run_dir.name}`", ""]
    run_summary = _read(run_dir / "run-summary.md")
    if run_summary:
        lines.extend(["## Outcome", "", *_summary_lines(run_summary), ""])

    if task_dir is None:
        lines.extend(["## Task", "", "- No task artifacts found.", ""])
        return "\n".join(lines)

    lines.extend(["## Task", "", f"- Directory: `{task_dir.relative_to(run_dir).as_posix()}`", ""])
    final_notes = _read(task_dir / "final-notes.md")
    if final_notes:
        lines.extend(["## Final Notes", "", *_summary_lines(final_notes), ""])

    stage_results = _read(task_dir / "stage-results.md")
    if stage_results:
        lines.extend(["## Stage Timeline", "", *_stage_lines(stage_results), ""])

    command_outputs = _command_outputs(task_dir)
    if command_outputs:
        lines.extend(["## Command And Test Output", ""])
        for path in command_outputs:
            lines.extend(_artifact_excerpt(path, task_dir, max_lines=34))
        lines.append("")

    diagnostics = sorted((task_dir / "diagnostics").glob("*.md")) if (task_dir / "diagnostics").exists() else []
    if diagnostics:
        lines.extend(["## Diagnostics", ""])
        for path in diagnostics[-5:]:
            lines.extend(_artifact_excerpt(path, task_dir, max_lines=18))
        lines.append("")

    debugger = task_dir / "debugger.md"
    if debugger.exists():
        lines.extend(["## Debugger", "", *_artifact_excerpt(debugger, task_dir, max_lines=24), ""])

    patches = _patch_attempts(task_dir)
    if patches:
        lines.extend(["## Code Attempts", ""])
        for path in patches:
            changed = _patch_changed_files(_read(path))
            summary = ", ".join(changed[:6]) if changed else "no changed files detected"
            if len(changed) > 6:
                summary += f", +{len(changed) - 6} more"
            lines.append(f"- `{path.name}`: {summary}")
        lines.append("")

    telemetry = task_dir / "telemetry-summary.md"
    if telemetry.exists():
        lines.extend(["## Model Attempts", "", *_artifact_excerpt(telemetry, task_dir, max_lines=28), ""])

    likely = _likely_cause(command_outputs, diagnostics, debugger)
    if likely:
        lines.extend(["## Likely Cause", "", likely, ""])

    return "\n".join(lines)


def _select_run_dir(runs_dir: Path, run_id: str) -> Path:
    if run_id == "latest":
        selected = latest_run_dir(runs_dir)
        if selected is None:
            raise NightShiftError(f"What happened error: no runs found under {runs_dir}")
        return selected
    selected = runs_dir / run_id
    if not selected.exists() or not selected.is_dir():
        raise NightShiftError(f"What happened error: run not found: {selected}")
    return selected


def _select_task_dir(run_dir: Path, task_id: str | None) -> Path | None:
    tasks_dir = run_dir / "tasks"
    if not tasks_dir.exists():
        return None
    if task_id:
        selected = tasks_dir / task_id
        if not selected.exists() or not selected.is_dir():
            raise NightShiftError(f"What happened error: task not found: {selected}")
        return selected
    candidates = [path for path in tasks_dir.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _summary_lines(text: str) -> list[str]:
    selected: list[str] = []
    wanted = ("- Task:", "- Status:", "- Retry count:", "- Reason:", "Task:", "Status:", "Retry count:", "Reason:")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(wanted):
            selected.append(stripped)
    return selected[:12] or ["- No summary lines found."]


def _stage_lines(text: str) -> list[str]:
    lines: list[str] = []
    current = ""
    status = ""
    reason = ""
    output = ""
    for raw in [*text.splitlines(), "## END"]:
        if raw.startswith("## "):
            if current:
                details = [status or "unknown"]
                if reason:
                    details.append(reason)
                if output:
                    details.append(f"artifact `{output}`")
                lines.append(f"- `{current}`: " + "; ".join(details))
            current = raw.removeprefix("## ").strip()
            status = ""
            reason = ""
            output = ""
        elif raw.startswith("Status:"):
            status = raw.removeprefix("Status:").strip()
        elif raw.startswith("Reason:"):
            reason = raw.removeprefix("Reason:").strip()
        elif raw.startswith("Output:"):
            output = raw.removeprefix("Output:").strip()
    return lines[:40] or ["- No stage results found."]


def _command_outputs(task_dir: Path) -> list[Path]:
    paths = [
        path
        for path in task_dir.glob("*output*.txt")
        if path.is_file() and not path.name.startswith("patch-apply-output")
    ]
    return sorted(paths, key=lambda path: path.stat().st_mtime)[-6:]


def _artifact_excerpt(path: Path, base: Path, *, max_lines: int) -> list[str]:
    text = _read(path)
    excerpt = _tail_relevant_lines(text, max_lines=max_lines)
    rel = path.relative_to(base).as_posix()
    return [f"### `{rel}`", "", "```text", *excerpt, "```", ""]


def _tail_relevant_lines(text: str, *, max_lines: int) -> list[str]:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return lines
    important = [
        line
        for line in lines
        if any(
            marker in line
            for marker in (
                "ERROR",
                "FAILED",
                "Traceback",
                "Exception",
                "Exit code:",
                "Command:",
                "ModuleNotFoundError",
                "ImportError",
                "NameError",
                "AssertionError",
                "Failure category:",
                "Probable root cause:",
                "Recommended next action:",
            )
        )
    ]
    if important:
        return important[-max_lines:]
    return lines[-max_lines:]


def _patch_attempts(task_dir: Path) -> list[Path]:
    names = ["proposed.patch", *[f"repair-{index}.patch" for index in range(1, 20)]]
    return [task_dir / name for name in names if (task_dir / name).exists()]


def _patch_changed_files(text: str) -> list[str]:
    files: list[str] = []
    for match in re.finditer(r"^diff --git a/(.*?) b/", text, flags=re.MULTILINE):
        path = match.group(1)
        if path not in files:
            files.append(path)
    return files


def _likely_cause(command_outputs: list[Path], diagnostics: list[Path], debugger: Path) -> str:
    combined = "\n".join([_read(path) for path in [*command_outputs, *diagnostics, debugger]])
    if "ModuleNotFoundError: No module named" in combined:
        return (
            "The latest command could not import a Python package. For src-layout projects, "
            "check that the command stage is using the project venv or that the project is installed editable."
        )
    if "NameError:" in combined:
        return "The latest implementation patch introduced a missing symbol or import."
    if "AssertionError" in combined or "FAILED" in combined:
        return "The tests ran but assertions failed; inspect the test output and latest repair patch."
    return ""
