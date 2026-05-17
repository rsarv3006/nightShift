from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from nightshift.artifacts import ArtifactStore
from nightshift.errors import SafetyError
from nightshift.git import ensure_clean_worktree, write_diff_artifact, write_git_artifacts


def git_available() -> bool:
    return shutil.which("git") is not None


@unittest.skipUnless(git_available(), "git is not available")
class GitSafetyTests(unittest.TestCase):
    def test_clean_worktree_requirement_blocks_dirty_repo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
            (root / "file.txt").write_text("dirty", encoding="utf-8")

            with self.assertRaisesRegex(SafetyError, "repository is dirty"):
                ensure_clean_worktree(root, True)

    def test_git_artifacts_are_written_for_repo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
            (root / "file.txt").write_text("dirty", encoding="utf-8")
            artifacts = ArtifactStore(root, ".nightshift", run_id="test-run")

            status_path = write_git_artifacts(artifacts, "TASK-001", "before")
            diff_path = write_diff_artifact(artifacts, "TASK-001")

            self.assertTrue(status_path.exists())
            self.assertTrue(diff_path.exists())
            self.assertIn("Git Status before", status_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
