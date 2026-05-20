"""Python project setup helper for integration sandboxes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import sys
import venv

from .errors import NightShiftError


@dataclass(frozen=True)
class SetupCommand:
    args: tuple[str, ...]
    cwd: Path


@dataclass(frozen=True)
class IntegrationSetupResult:
    project_dir: Path
    venv_dir: Path
    python: Path
    created_venv: bool
    commands: tuple[SetupCommand, ...]
    dry_run: bool = False


def setup_python_project(
    project_dir: str | Path = ".",
    *,
    nightshift_root: str | Path | None = None,
    extras: tuple[str, ...] = ("pytest",),
    create_venv: bool = True,
    validate: bool = True,
    dry_run: bool = False,
) -> IntegrationSetupResult:
    """Install NightShift and a Python target project into an integration venv."""

    project = Path(project_dir).resolve()
    if not project.exists() or not project.is_dir():
        raise NightShiftError(f"Integration setup error: project directory does not exist: {project}")

    venv_dir, created = _ensure_venv(project, create=create_venv, dry_run=dry_run)
    python = _venv_python(venv_dir)
    root = Path(nightshift_root).resolve() if nightshift_root else _default_nightshift_root()
    if not root.exists():
        raise NightShiftError(f"Integration setup error: NightShift root does not exist: {root}")

    commands = [
        SetupCommand((str(python), "-m", "pip", "install", "-e", str(root)), project),
        SetupCommand((str(python), "-m", "pip", "install", "-e", str(project)), project),
    ]
    if extras:
        commands.append(SetupCommand((str(python), "-m", "pip", "install", *extras), project))
    if validate and (project / "nightshift.yaml").exists():
        commands.append(SetupCommand((str(python), "-m", "nightshift.cli", "validate"), project))

    if not dry_run:
        for command in commands:
            completed = subprocess.run(
                command.args,
                cwd=command.cwd,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if completed.returncode != 0:
                rendered = " ".join(command.args)
                raise NightShiftError(
                    f"Integration setup error: command failed with code {completed.returncode}: {rendered}"
                )

    return IntegrationSetupResult(
        project_dir=project,
        venv_dir=venv_dir,
        python=python,
        created_venv=created,
        commands=tuple(commands),
        dry_run=dry_run,
    )


def format_setup_result(result: IntegrationSetupResult) -> str:
    lines = [
        f"Project: {result.project_dir}",
        f"Venv: {result.venv_dir}",
        f"Python: {result.python}",
        f"Created venv: {str(result.created_venv).lower()}",
    ]
    if result.dry_run:
        lines.append("Dry run: true")
        lines.append("Commands:")
        for command in result.commands:
            lines.append(f"- ({command.cwd}) {' '.join(command.args)}")
    else:
        lines.append("Setup complete.")
        lines.append("Run from the project directory:")
        lines.append(f"  {result.python} -m nightshift.cli run --task TASK-001")
    return "\n".join(lines)


def _ensure_venv(project: Path, *, create: bool, dry_run: bool) -> tuple[Path, bool]:
    candidates = _venv_candidates(project)
    for candidate in candidates:
        if _venv_python(candidate).exists():
            return candidate, False
    if not create:
        raise NightShiftError(
            "Integration setup error: no virtual environment found. "
            f"Checked: {', '.join(str(path) for path in candidates)}"
        )
    target = candidates[0]
    if not dry_run:
        venv.EnvBuilder(with_pip=True).create(target)
    return target, True


def _venv_candidates(project: Path) -> tuple[Path, ...]:
    if project.name == "project" and project.parent.name:
        return (project.parent / ".venv", project / ".venv")
    return (project / ".venv", project.parent / ".venv")


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _default_nightshift_root() -> Path:
    return Path(__file__).resolve().parents[1]
