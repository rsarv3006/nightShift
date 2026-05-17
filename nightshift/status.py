"""Project status inspection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import NightShiftConfig
from .tasks import Task, dependency_problems, select_next_runnable_task


@dataclass(frozen=True)
class ProjectStatus:
    config_path: Path
    project_root: Path
    task_count: int
    completed_count: int
    incomplete_count: int
    next_task_id: str | None
    latest_run_dir: Path | None
    warnings: tuple[str, ...]


def build_status(config: NightShiftConfig, tasks: list[Task]) -> ProjectStatus:
    latest = latest_run_dir(config.project.root / config.project.artifact_dir / "runs")
    warnings = dependency_problems(tasks)
    try:
        next_task = select_next_runnable_task(tasks)
        next_task_id = next_task.id
    except Exception:
        next_task_id = None
    completed = sum(1 for task in tasks if task.completed)
    return ProjectStatus(
        config_path=config.path,
        project_root=config.project.root,
        task_count=len(tasks),
        completed_count=completed,
        incomplete_count=len(tasks) - completed,
        next_task_id=next_task_id,
        latest_run_dir=latest,
        warnings=tuple(warnings),
    )


def latest_run_dir(runs_dir: Path) -> Path | None:
    if not runs_dir.exists() or not runs_dir.is_dir():
        return None
    candidates = [path for path in runs_dir.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def format_status(status: ProjectStatus) -> str:
    lines = [
        f"Config: {status.config_path}",
        f"Project root: {status.project_root}",
        f"Tasks: {status.task_count}",
        f"Completed tasks: {status.completed_count}",
        f"Incomplete tasks: {status.incomplete_count}",
        f"Next task: {status.next_task_id or '<none>'}",
        f"Latest run: {status.latest_run_dir or '<none>'}",
    ]
    if status.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in status.warnings)
    return "\n".join(lines)
