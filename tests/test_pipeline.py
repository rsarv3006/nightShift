from pathlib import Path
import tempfile
import unittest

from nightshift.artifacts import ArtifactStore
from nightshift.config import (
    AgentConfig,
    NightShiftConfig,
    PipelineConfig,
    ProjectConfig,
    SafetyConfig,
    StageConfig,
)
from nightshift.pipeline import PipelineRunner
from nightshift.tasks import parse_tasks


TASK_MD = """# Tasks

- [ ] TASK-001: Run fake pipeline

Description:
Exercise a fake pipeline.

Acceptance Criteria:
- Happy path completes
- Artifacts are written
"""


def make_config(root: Path, stages: tuple[StageConfig, ...], max_retries: int = 2) -> NightShiftConfig:
    return NightShiftConfig(
        path=root / "nightshift.yaml",
        project=ProjectConfig(
            name="test",
            root=root,
            task_file=Path("tasks.md"),
            artifact_dir=Path(".nightshift"),
        ),
        safety=SafetyConfig(
            require_clean_worktree=False,
            scoped_paths=(".",),
            allowed_commands=('python -c "print(\'tests ok\')"',),
            forbidden_commands=("rm -rf",),
        ),
        agents={
            "planner": AgentConfig(
                id="planner",
                backend="command",
                command='python -c "print(\'plan ok\')"',
                system_prompt=Path("planner.md"),
            ),
            "reviewer": AgentConfig(
                id="reviewer",
                backend="command",
                command='python -c "print(\'status: pass\\nreason: ok\')"',
                system_prompt=Path("reviewer.md"),
            ),
            "retry_reviewer": AgentConfig(
                id="retry_reviewer",
                backend="command",
                command='python -c "print(\'status: retry\\nreason: retry it\\nnext_stage: implement\')"',
                system_prompt=Path("reviewer.md"),
            ),
        },
        pipeline=PipelineConfig(max_task_retries=max_retries, stages=stages),
    )


class PipelineRunnerTests(unittest.TestCase):
    def test_happy_path_pipeline_completes_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_common_files(root)
            stages = (
                StageConfig(id="plan", type="agent", agent="planner", output="plan.md"),
                StageConfig(
                    id="test",
                    type="command",
                    commands=('python -c "print(\'tests ok\')"',),
                    output="test-output.txt",
                ),
                StageConfig(id="review", type="agent_review", agent="reviewer", output="review.md"),
                StageConfig(id="summarize", type="summarize", output="final-notes.md"),
            )
            config = make_config(root, stages)
            runner = PipelineRunner(config, ArtifactStore(root, ".nightshift", run_id="test-run"))
            task = parse_tasks(TASK_MD)[0]

            result = runner.run_task(task)

            self.assertEqual(result.status, "complete")
            self.assertEqual(result.retry_count, 0)
            self.assertTrue((root / ".nightshift" / "runs" / "test-run" / "tasks" / task.id / "plan.md").exists())
            self.assertTrue((root / ".nightshift" / "runs" / "test-run" / "tasks" / task.id / "stage-results.md").exists())
            self.assertTrue((root / ".nightshift" / "runs" / "test-run" / "tasks" / task.id / "context.md").exists())
            self.assertTrue((root / ".nightshift" / "runs" / "test-run" / "tasks" / task.id / "context-out.md").exists())
            self.assertIn(
                "## Task Context",
                (root / ".nightshift" / "runs" / "test-run" / "tasks" / task.id / "plan.md").read_text(encoding="utf-8"),
            )
            self.assertIn("Modified Files", (root / ".nightshift" / "runs" / "test-run" / "run-summary.md").read_text(encoding="utf-8"))

    def test_review_can_retry_implementation_until_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_common_files(root)
            stages = (
                StageConfig(id="implement", type="agent", agent="planner", output="implementation-log.md"),
                StageConfig(
                    id="review",
                    type="agent_review",
                    agent="retry_reviewer",
                    on_fail="implement",
                    output="review.md",
                ),
            )
            config = make_config(root, stages, max_retries=2)
            runner = PipelineRunner(config, ArtifactStore(root, ".nightshift", run_id="test-run"))
            task = parse_tasks(TASK_MD)[0]

            result = runner.run_task(task)

            self.assertEqual(result.status, "failed")
            self.assertEqual(result.retry_count, 2)
            self.assertIn("Retry limit reached", result.reason)
            self.assertEqual([item.stage_id for item in result.stage_results], ["implement", "review", "implement", "review", "implement", "review"])


def _write_common_files(root: Path) -> None:
    (root / "nightshift.yaml").write_text("project:\n  name: test\n", encoding="utf-8")
    (root / "tasks.md").write_text(TASK_MD, encoding="utf-8")
    (root / "planner.md").write_text("Plan.", encoding="utf-8")
    (root / "reviewer.md").write_text("Review.", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
