from pathlib import Path
import tempfile
import unittest

from nightshift.errors import TaskError
from nightshift.tasks import (
    dependency_problems,
    ensure_dependencies_satisfied,
    mark_task_completed,
    parse_task_file,
    parse_tasks,
    select_next_incomplete_task,
    select_next_runnable_task,
    select_task_by_id,
    validate_task_dependencies,
)


TASKS_MD = """# Tasks

- [x] TASK-001: Completed task

Description:
Already done.

Acceptance Criteria:
- It is complete

- [ ] TASK-002: Add artifact directory creation

Description:
Create per-run and per-task artifact directories.

Dependencies:
- TASK-001

Acceptance Criteria:
- Creates `.nightshift/runs/<timestamp>/`
- Creates task-specific folder
- Writes task snapshot
"""


class TaskParserTests(unittest.TestCase):
    def test_parse_documented_task_format(self) -> None:
        tasks = parse_tasks(TASKS_MD)

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[1].id, "TASK-002")
        self.assertEqual(tasks[1].title, "Add artifact directory creation")
        self.assertFalse(tasks[1].completed)
        self.assertEqual(
            tasks[1].description,
            "Create per-run and per-task artifact directories.",
        )
        self.assertEqual(tasks[1].dependencies, ("TASK-001",))
        self.assertEqual(len(tasks[1].acceptance_criteria), 3)
        self.assertIn("TASK-002", tasks[1].raw_markdown)

    def test_select_next_incomplete_task(self) -> None:
        tasks = parse_tasks(TASKS_MD)

        selected = select_next_incomplete_task(tasks)

        self.assertEqual(selected.id, "TASK-002")

    def test_select_task_by_id(self) -> None:
        tasks = parse_tasks(TASKS_MD)

        selected = select_task_by_id(tasks, "TASK-001")

        self.assertTrue(selected.completed)

    def test_select_task_by_id_reports_available_tasks(self) -> None:
        tasks = parse_tasks(TASKS_MD)

        with self.assertRaisesRegex(TaskError, "Available tasks: TASK-001, TASK-002"):
            select_task_by_id(tasks, "TASK-999")

    def test_parse_task_file_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with self.assertRaisesRegex(TaskError, "outside project root"):
                parse_task_file(root, "../tasks.md")

    def test_malformed_task_header_has_useful_error(self) -> None:
        markdown = """# Tasks

- [ ] Add YAML config loading

Acceptance Criteria:
- Loads config
"""

        with self.assertRaisesRegex(TaskError, "malformed task header"):
            parse_tasks(markdown)

    def test_missing_acceptance_criteria_fails(self) -> None:
        markdown = """# Tasks

- [ ] TASK-001: Missing criteria

Description:
No acceptance criteria.
"""

        with self.assertRaisesRegex(TaskError, "missing Acceptance Criteria"):
            parse_tasks(markdown)

    def test_no_tasks_fails(self) -> None:
        with self.assertRaisesRegex(TaskError, "no tasks found"):
            parse_tasks("# Tasks\n\nNothing here.\n")

    def test_dependency_blocks_specific_task_selection(self) -> None:
        tasks = parse_tasks(TASKS_MD.replace("[x] TASK-001", "[ ] TASK-001"))

        with self.assertRaisesRegex(TaskError, "blocked by incomplete dependencies"):
            ensure_dependencies_satisfied(tasks, tasks[1])

    def test_select_next_runnable_skips_blocked_tasks(self) -> None:
        markdown = TASKS_MD.replace("[x] TASK-001", "[ ] TASK-001")
        tasks = parse_tasks(markdown)

        selected = select_next_runnable_task(tasks)

        self.assertEqual(selected.id, "TASK-001")

    def test_dependency_validation_reports_missing_and_cycles(self) -> None:
        markdown = """# Tasks

- [ ] TASK-001: First

Dependencies:
- TASK-002

Acceptance Criteria:
- ok

- [ ] TASK-002: Second

Dependencies:
- TASK-001
- TASK-999

Acceptance Criteria:
- ok
"""
        tasks = parse_tasks(markdown)

        problems = dependency_problems(tasks)

        self.assertTrue(any("TASK-999" in problem for problem in problems))
        self.assertTrue(any("cycle" in problem.lower() for problem in problems))
        with self.assertRaisesRegex(TaskError, "Task dependency error"):
            validate_task_dependencies(tasks)

    def test_mark_task_completed_updates_only_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = root / "tasks.md"
            task_path.write_text(TASKS_MD, encoding="utf-8")

            changed = mark_task_completed(root, "tasks.md", "TASK-002")

            self.assertTrue(changed)
            content = task_path.read_text(encoding="utf-8")
            self.assertIn("- [x] TASK-002: Add artifact directory creation", content)


if __name__ == "__main__":
    unittest.main()
