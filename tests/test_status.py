from pathlib import Path
import tempfile
import unittest

from nightshift.artifacts import ArtifactStore
from nightshift.config import load_config
from nightshift.init import init_project
from nightshift.status import build_status, format_status
from nightshift.tasks import parse_task_file


class StatusTests(unittest.TestCase):
    def test_status_reports_counts_and_latest_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_project(root)
            ArtifactStore(root, ".nightshift", run_id="run-a").initialize_run()
            config = load_config(root / "nightshift.yaml")
            tasks = parse_task_file(config.project.root, config.project.task_file)

            status = build_status(config, tasks)
            output = format_status(status)

            self.assertEqual(status.task_count, 1)
            self.assertEqual(status.incomplete_count, 1)
            self.assertEqual(status.next_task_id, "TASK-001")
            self.assertIsNotNone(status.latest_run_dir)
            self.assertIn("Project root:", output)
            self.assertIn("Latest run:", output)


if __name__ == "__main__":
    unittest.main()
