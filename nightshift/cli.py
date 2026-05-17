"""Command line interface for NightShift."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import validate_config
from .errors import NightShiftError
from .init import init_project
from .pipeline import PipelineRunner
from .tasks import parse_task_file, select_next_incomplete_task, select_task_by_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nightshift", description="Auditable AI pipeline runner.")
    parser.add_argument("--version", action="version", version="nightshift 0.1.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create starter NightShift files.")
    init_parser.add_argument("--root", default=".", help="Directory to initialize.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing starter files.")

    validate_parser = subparsers.add_parser("validate", help="Validate nightshift.yaml.")
    validate_parser.add_argument("--config", default="nightshift.yaml", help="Config file to validate.")

    run_parser = subparsers.add_parser("run", help="Run the configured pipeline for one task.")
    run_parser.add_argument("--config", default="nightshift.yaml", help="Config file to use.")
    run_parser.add_argument("--task", help="Specific task id to run.")

    subparsers.add_parser("status", help="Status reporting is planned for a later phase.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            written = init_project(Path(args.root), force=args.force)
            print("Created NightShift starter files:")
            for path in written:
                print(f"- {path}")
            return 0

        if args.command == "validate":
            config = validate_config(args.config)
            tasks = parse_task_file(config.project.root, config.project.task_file)
            incomplete = sum(1 for task in tasks if not task.completed)
            print(f"Config valid: {config.path}")
            print(f"Project: {config.project.name}")
            print(f"Stages: {len(config.pipeline.stages)}")
            print(f"Tasks: {len(tasks)}")
            print(f"Incomplete tasks: {incomplete}")
            return 0

        if args.command == "run":
            config = validate_config(args.config)
            tasks = parse_task_file(config.project.root, config.project.task_file)
            task = select_task_by_id(tasks, args.task) if args.task else select_next_incomplete_task(tasks)
            result = PipelineRunner(config).run_task(task)
            print(f"Task: {result.task_id}")
            print(f"Status: {result.status}")
            print(f"Retries: {result.retry_count}")
            print(f"Artifacts: {result.artifact_dir}")
            print(f"Reason: {result.reason}")
            return 0 if result.status == "complete" else 1

        if args.command in {"status"}:
            parser.error(f"'{args.command}' is not implemented yet.")

    except NightShiftError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
