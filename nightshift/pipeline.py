"""Deterministic pipeline runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .agents import AgentExecutor
from .artifacts import ArtifactStore
from .commands import CommandExecutor
from .config import COMMAND_STAGE_TYPES, NightShiftConfig, StageConfig
from .context import ContextManager
from .errors import PipelineError
from .reports import ReportGenerator
from .stages import StageResult
from .tasks import Task


@dataclass(frozen=True)
class PipelineResult:
    task_id: str
    status: str
    retry_count: int
    stage_results: tuple[StageResult, ...]
    artifact_dir: str
    reason: str


class PipelineRunner:
    """Execute configured stages for one task."""

    def __init__(
        self,
        config: NightShiftConfig,
        artifacts: ArtifactStore | None = None,
        agent_timeout_seconds: int = 600,
        command_timeout_seconds: int = 300,
    ) -> None:
        self.config = config
        self.artifacts = artifacts or ArtifactStore.from_config(config)
        self.context = ContextManager(self.artifacts)
        self.reports = ReportGenerator(config.project.root, self.artifacts)
        self.agent_executor = AgentExecutor(
            config.project.root,
            config.agents,
            self.artifacts,
            timeout_seconds=agent_timeout_seconds,
        )
        self.command_executor = CommandExecutor(
            config.project.root,
            config.safety,
            self.artifacts,
            timeout_seconds=command_timeout_seconds,
        )

    def run_task(self, task: Task) -> PipelineResult:
        self.artifacts.initialize_run()
        self.artifacts.write_config_snapshot(self.config.path)
        self.artifacts.write_task_snapshot(task)
        self.context.ensure_project_context()
        self.context.create_task_context(task)

        stages = list(self.config.pipeline.stages)
        stage_indexes = {stage.id: index for index, stage in enumerate(stages)}
        stage_results: list[StageResult] = []
        previous_outputs: dict[str, str] = {}
        retry_notes: list[str] = []
        retry_count = 0
        index = 0
        final_status = "complete"
        final_reason = "Pipeline completed."

        while index < len(stages):
            stage = stages[index]
            result = self._run_stage(stage, task, previous_outputs, retry_notes)
            stage_results.append(result)
            previous_outputs[stage.id] = self._read_output(result.output_path)
            if result.context_update:
                retry_notes.append(f"Context update from '{stage.id}': {result.context_update}")

            if result.status == "pass":
                index += 1
                continue

            target_stage = stage.on_fail or result.next_stage
            if target_stage:
                if retry_count >= self.config.pipeline.max_task_retries:
                    final_status = "failed"
                    final_reason = (
                        f"Retry limit reached after stage '{stage.id}': {result.reason}"
                    )
                    break
                if target_stage not in stage_indexes:
                    final_status = "failed"
                    final_reason = (
                        f"Stage '{stage.id}' requested unknown next stage '{target_stage}'."
                    )
                    break
                retry_count += 1
                retry_notes.append(
                    f"Retry {retry_count}: stage '{stage.id}' returned "
                    f"{result.status} ({result.reason}); redirecting to '{target_stage}'."
                )
                index = stage_indexes[target_stage]
                continue

            final_status = "failed"
            final_reason = f"Stage '{stage.id}' returned {result.status}: {result.reason}"
            break

        context_out_path = self.context.write_context_out(
            task,
            final_status,
            final_reason,
            retry_notes,
            durable_notes=[
                result.context_update
                for result in stage_results
                if result.context_update
            ],
        )
        self.reports.write_reports(
            task,
            final_status,
            final_reason,
            retry_count,
            stage_results,
            context_out_path=context_out_path,
        )

        return PipelineResult(
            task_id=task.id,
            status=final_status,
            retry_count=retry_count,
            stage_results=tuple(stage_results),
            artifact_dir=str(self.artifacts.create_task_dir(task.id).directory.relative_to(self.config.project.root)),
            reason=final_reason,
        )

    def _run_stage(
        self,
        stage: StageConfig,
        task: Task,
        previous_outputs: dict[str, str],
        retry_notes: list[str],
    ) -> StageResult:
        if stage.type in {"agent", "agent_review", "review"}:
            context = self.context.read_context(task, retry_notes)
            return self.agent_executor.run_stage(
                stage,
                task,
                previous_outputs,
                retry_notes,
                project_context=context.project_context,
                task_context=context.task_context,
                retry_context=context.retry_context,
            )
        if stage.type in COMMAND_STAGE_TYPES:
            return self.command_executor.run_stage(stage, task.id)
        if stage.type == "summarize":
            output_path = self.artifacts.write_stage_output(
                task.id,
                stage.output or "final-notes.md",
                format_summary_stage(task, previous_outputs, retry_notes),
            )
            return StageResult(
                stage_id=stage.id,
                status="pass",
                reason="Summary written.",
                output_path=str(output_path.relative_to(self.config.project.root)),
            )
        raise PipelineError(f"Pipeline error: unsupported stage type '{stage.type}'.")

    def _read_output(self, output_path: str | None) -> str:
        if output_path is None:
            return ""
        path = self.config.project.root / Path(output_path)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

def format_summary_stage(
    task: Task,
    previous_outputs: dict[str, str],
    retry_notes: list[str],
) -> str:
    outputs = "\n".join(f"- {stage_id}" for stage_id in previous_outputs)
    retries = "\n".join(f"- {note}" for note in retry_notes) or "- None"
    return "\n".join(
        [
            "# Final Notes",
            "",
            f"Task: `{task.id}`",
            f"Title: {task.title}",
            "",
            "## Stage Outputs",
            "",
            outputs or "- None",
            "",
            "## Retry Notes",
            "",
            retries,
            "",
        ]
    )

