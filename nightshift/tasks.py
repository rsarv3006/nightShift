"""Markdown task parsing and selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .errors import SafetyError, TaskError
from .safety import resolve_inside_root


TASK_HEADER_RE = re.compile(r"^\s*-\s+\[(?P<mark>[ xX])\]\s+(?P<id>[A-Z]+-\d+):\s+(?P<title>.+?)\s*$")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[[^\]]*\]")
SECTION_RE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z ]+):\s*$")


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    completed: bool
    description: str
    acceptance_criteria: tuple[str, ...]
    dependencies: tuple[str, ...]
    raw_markdown: str
    line_number: int


def parse_task_file(project_root: str | Path, task_file: str | Path) -> list[Task]:
    """Load and parse a task markdown file inside the project root."""

    try:
        path = resolve_inside_root(project_root, task_file, "task file")
    except SafetyError as exc:
        raise TaskError(str(exc)) from exc

    if not path.exists():
        raise TaskError(f"Task error: task file does not exist: {path}")

    return parse_tasks(path.read_text(encoding="utf-8"))


def task_file_path(project_root: str | Path, task_file: str | Path) -> Path:
    try:
        return resolve_inside_root(project_root, task_file, "task file")
    except SafetyError as exc:
        raise TaskError(str(exc)) from exc


def parse_tasks(markdown: str) -> list[Task]:
    """Parse NightShift's documented markdown checklist task format."""

    lines = markdown.splitlines()
    tasks: list[Task] = []
    seen_ids: set[str] = set()
    index = 0

    while index < len(lines):
        line = lines[index]
        header = TASK_HEADER_RE.match(line)
        if not header:
            if CHECKBOX_RE.match(line):
                raise TaskError(
                    f"Task error: malformed task header on line {index + 1}. "
                    "Expected '- [ ] TASK-001: Task title'."
                )
            index += 1
            continue

        task_id = header.group("id")
        if task_id in seen_ids:
            raise TaskError(f"Task error: duplicate task id '{task_id}' on line {index + 1}.")
        seen_ids.add(task_id)

        start = index
        index += 1
        while index < len(lines) and not TASK_HEADER_RE.match(lines[index]):
            if CHECKBOX_RE.match(lines[index]):
                raise TaskError(
                    f"Task error: malformed task header on line {index + 1}. "
                    "Expected '- [ ] TASK-001: Task title'."
                )
            index += 1

        block = lines[start:index]
        description = _extract_section(block, "Description")
        acceptance_criteria = tuple(_extract_bullets(block, "Acceptance Criteria"))
        dependencies = tuple(_extract_bullets(block, "Dependencies"))

        if not acceptance_criteria:
            raise TaskError(
                f"Task error: task '{task_id}' is missing Acceptance Criteria bullets."
            )

        tasks.append(
            Task(
                id=task_id,
                title=header.group("title"),
                completed=header.group("mark").lower() == "x",
                description=description,
                acceptance_criteria=acceptance_criteria,
                dependencies=dependencies,
                raw_markdown="\n".join(block).strip() + "\n",
                line_number=start + 1,
            )
        )

    if not tasks:
        raise TaskError("Task error: no tasks found. Expected '- [ ] TASK-001: Task title'.")

    return tasks


def select_next_incomplete_task(tasks: list[Task] | tuple[Task, ...]) -> Task:
    """Return the first incomplete task in file order."""

    for task in tasks:
        if not task.completed:
            return task
    raise TaskError("Task error: no incomplete tasks found.")


def select_next_runnable_task(tasks: list[Task] | tuple[Task, ...]) -> Task:
    """Return the first incomplete task whose dependencies are complete."""

    completed = {task.id for task in tasks if task.completed}
    blocked: list[str] = []
    for task in tasks:
        if task.completed:
            continue
        missing = [dependency for dependency in task.dependencies if dependency not in completed]
        if missing:
            blocked.append(f"{task.id} blocked by {', '.join(missing)}")
            continue
        return task
    if blocked:
        raise TaskError("Task error: no runnable incomplete tasks. " + "; ".join(blocked))
    raise TaskError("Task error: no incomplete tasks found.")


def select_task_by_id(tasks: list[Task] | tuple[Task, ...], task_id: str) -> Task:
    """Return a task by id."""

    for task in tasks:
        if task.id == task_id:
            return task
    available = ", ".join(task.id for task in tasks) or "<none>"
    raise TaskError(f"Task error: unknown task id '{task_id}'. Available tasks: {available}.")


def ensure_dependencies_satisfied(tasks: list[Task] | tuple[Task, ...], task: Task) -> None:
    task_ids = {candidate.id for candidate in tasks}
    completed = {candidate.id for candidate in tasks if candidate.completed}
    missing_refs = [dependency for dependency in task.dependencies if dependency not in task_ids]
    if missing_refs:
        raise TaskError(
            f"Task error: task '{task.id}' references missing dependencies: "
            f"{', '.join(missing_refs)}."
        )
    incomplete = [dependency for dependency in task.dependencies if dependency not in completed]
    if incomplete:
        raise TaskError(
            f"Task error: task '{task.id}' is blocked by incomplete dependencies: "
            f"{', '.join(incomplete)}."
        )


def dependency_problems(tasks: list[Task] | tuple[Task, ...]) -> list[str]:
    task_ids = {task.id for task in tasks}
    problems: list[str] = []
    for task in tasks:
        for dependency in task.dependencies:
            if dependency not in task_ids:
                problems.append(f"Task '{task.id}' references missing dependency '{dependency}'.")
    problems.extend(_cycle_problems(tasks))
    return problems


def validate_task_dependencies(tasks: list[Task] | tuple[Task, ...]) -> None:
    problems = dependency_problems(tasks)
    if problems:
        raise TaskError("Task dependency error: " + " ".join(problems))


def mark_task_completed(project_root: str | Path, task_file: str | Path, task_id: str) -> bool:
    """Mark a task complete in the markdown task file with a minimal line edit."""

    path = task_file_path(project_root, task_file)
    if not path.exists():
        raise TaskError(f"Task error: task file does not exist: {path}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = TASK_HEADER_RE.match(line.rstrip("\r\n"))
        if match and match.group("id") == task_id:
            if match.group("mark").lower() == "x":
                return False
            lines[index] = re.sub(r"\[[ ]\]", "[x]", line, count=1)
            path.write_text("".join(lines), encoding="utf-8")
            return True
    raise TaskError(f"Task error: cannot mark unknown task complete: {task_id}.")


def _extract_section(block: list[str], section_name: str) -> str:
    start = _find_section_index(block, section_name)
    if start is None:
        return ""

    collected: list[str] = []
    for line in block[start + 1 :]:
        if SECTION_RE.match(line.strip()):
            break
        collected.append(line)

    return "\n".join(collected).strip()


def _extract_bullets(block: list[str], section_name: str) -> list[str]:
    start = _find_section_index(block, section_name)
    if start is None:
        return []

    bullets: list[str] = []
    for line in block[start + 1 :]:
        stripped = line.strip()
        if SECTION_RE.match(stripped):
            break
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value:
                bullets.append(value)
    return bullets


def _find_section_index(block: list[str], section_name: str) -> int | None:
    expected = f"{section_name}:".lower()
    for index, line in enumerate(block):
        if line.strip().lower() == expected:
            return index
    return None


def _cycle_problems(tasks: list[Task] | tuple[Task, ...]) -> list[str]:
    graph = {task.id: tuple(dep for dep in task.dependencies if dep in {item.id for item in tasks}) for task in tasks}
    visiting: set[str] = set()
    visited: set[str] = set()
    problems: list[str] = []

    def visit(task_id: str, path: list[str]) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            cycle_start = path.index(task_id) if task_id in path else 0
            cycle = " -> ".join(path[cycle_start:] + [task_id])
            problems.append(f"Dependency cycle detected: {cycle}.")
            return
        visiting.add(task_id)
        for dependency in graph.get(task_id, ()):
            visit(dependency, path + [dependency])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id, [task_id])
    return problems
