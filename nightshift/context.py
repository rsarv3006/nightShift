"""Context file management for pipeline runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .artifacts import ArtifactStore
from .tasks import Task


@dataclass(frozen=True)
class TaskContext:
    project_context: str
    task_context: str
    retry_context: str


class ContextManager:
    """Create and read compact context files for one run."""

    def __init__(self, artifacts: ArtifactStore) -> None:
        self.artifacts = artifacts

    def ensure_project_context(self) -> Path:
        self.artifacts.initialize_run()
        if not self.artifacts.project_context_path.exists():
            self.artifacts.project_context_path.write_text("# Project Context\n\n", encoding="utf-8")
        return self.artifacts.project_context_path

    def create_task_context(self, task: Task) -> Path:
        self.ensure_project_context()
        content = "\n".join(
            [
                "# Task Context",
                "",
                f"Task: `{task.id}`",
                f"Title: {task.title}",
                "",
                "## Description",
                "",
                task.description or "_No description provided._",
                "",
                "## Acceptance Criteria",
                "",
                "\n".join(f"- {item}" for item in task.acceptance_criteria),
                "",
            ]
        )
        return self.artifacts.write_stage_output(task.id, "context.md", content)

    def read_context(self, task: Task, retry_notes: list[str] | None = None) -> TaskContext:
        project_path = self.ensure_project_context()
        task_context_path = self.artifacts.create_task_dir(task.id).directory / "context.md"
        if not task_context_path.exists():
            task_context_path = self.create_task_context(task)

        retries = retry_notes or []
        return TaskContext(
            project_context=project_path.read_text(encoding="utf-8"),
            task_context=task_context_path.read_text(encoding="utf-8"),
            retry_context="\n".join(f"- {note}" for note in retries) if retries else "- None",
        )

    def write_context_out(
        self,
        task: Task,
        status: str,
        reason: str,
        retry_notes: list[str],
        durable_notes: list[str] | None = None,
    ) -> Path:
        notes = durable_notes or []
        content = "\n".join(
            [
                "# Context Out",
                "",
                f"Task: `{task.id}`",
                f"Status: {status}",
                f"Reason: {reason}",
                "",
                "## Retry Notes",
                "",
                "\n".join(f"- {note}" for note in retry_notes) if retry_notes else "- None",
                "",
                "## Durable Notes",
                "",
                "\n".join(f"- {note}" for note in notes) if notes else "- None",
                "",
            ]
        )
        return self.artifacts.write_stage_output(task.id, "context-out.md", content)

    def append_project_context(self, task: Task, notes: list[str]) -> None:
        if not notes:
            return
        path = self.ensure_project_context()
        addition = "\n".join(
            [
                f"## {task.id}",
                "",
                *[f"- {note}" for note in notes],
                "",
            ]
        )
        existing = path.read_text(encoding="utf-8")
        path.write_text(existing.rstrip() + "\n\n" + addition, encoding="utf-8")
