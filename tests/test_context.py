from pathlib import Path
import tempfile
import unittest

from nightshift.artifacts import ArtifactStore
from nightshift.context import ContextManager
from nightshift.tasks import parse_tasks


TASK_MD = """# Tasks

- [ ] TASK-001: Build context

Description:
Create compact task context.

Acceptance Criteria:
- Context files are created
- Retry notes are persisted
"""


class ContextManagerTests(unittest.TestCase):
    def test_creates_project_task_and_context_out_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = ArtifactStore(root, ".nightshift", run_id="test-run")
            manager = ContextManager(artifacts)
            task = parse_tasks(TASK_MD)[0]

            project_path = manager.ensure_project_context()
            task_path = manager.create_task_context(task)
            context = manager.read_context(task, ["retry once"])
            out_path = manager.write_context_out(task, "complete", "done", ["retry once"], ["useful fact"])

            self.assertTrue(project_path.exists())
            self.assertTrue(task_path.exists())
            self.assertTrue(out_path.exists())
            self.assertIn("TASK-001", context.task_context)
            self.assertIn("retry once", context.retry_context)
            self.assertIn("useful fact", out_path.read_text(encoding="utf-8"))

    def test_append_project_context_adds_durable_notes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manager = ContextManager(ArtifactStore(root, ".nightshift", run_id="test-run"))
            task = parse_tasks(TASK_MD)[0]

            manager.append_project_context(task, ["Remember this"])

            content = (root / ".nightshift" / "project-context.md").read_text(encoding="utf-8")
            self.assertIn("TASK-001", content)
            self.assertIn("Remember this", content)


if __name__ == "__main__":
    unittest.main()
