"""Run telemetry aggregation."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TelemetryEntry:
    stage_id: str
    stage_type: str
    status: str
    agent_id: str | None
    model: str | None
    duration_seconds: float
    prompt_tokens: int
    output_tokens: int
    retry_count: int
    actual_prompt_tokens: int | None = None
    actual_output_tokens: int | None = None


def telemetry_from_stage_output(
    *,
    stage_id: str,
    stage_type: str,
    status: str,
    output: str,
    retry_count: int,
    agent_id: str | None = None,
    model: str | None = None,
) -> TelemetryEntry:
    parsed_agent = _field(output, "Agent") or agent_id
    duration = _float_field(output, "Duration seconds")
    prompt = _section(output, "Prompt")
    stdout = _section(output, "stdout")
    stderr = _section(output, "stderr")
    if not prompt:
        prompt = ""
    if not stdout and not stderr:
        stdout = output

    actual_prompt = _int_field(output, "Prompt tokens")
    actual_output = _int_field(output, "Output tokens")

    if actual_prompt is not None and actual_output is not None:
        prompt_tokens = actual_prompt
        output_tokens = actual_output
    else:
        prompt_tokens = estimate_tokens(prompt)
        output_tokens = estimate_tokens("\n".join([stdout, stderr]))

    return TelemetryEntry(
        stage_id=stage_id,
        stage_type=stage_type,
        status=status,
        agent_id=parsed_agent,
        model=model,
        duration_seconds=duration,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        retry_count=retry_count,
        actual_prompt_tokens=actual_prompt,
        actual_output_tokens=actual_output,
    )


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(re.findall(r"\S+", text)) * 4 + 2) // 3)


def format_telemetry_summary(entries: tuple[TelemetryEntry, ...]) -> str:
    total_duration = sum(entry.duration_seconds for entry in entries)
    total_prompt = sum(entry.prompt_tokens for entry in entries)
    total_output = sum(entry.output_tokens for entry in entries)
    all_actual = all(entry.actual_prompt_tokens is not None and entry.actual_output_tokens is not None for entry in entries)
    failures = sum(1 for entry in entries if entry.status != "pass")
    lines = [
        "# Telemetry Summary",
        "",
        f"Stages observed: {len(entries)}",
        f"Failures observed: {failures}",
        f"Total runtime seconds: {total_duration:.3f}",
    ]
    if all_actual:
        lines.append(f"Total prompt tokens: {total_prompt}")
        lines.append(f"Total output tokens: {total_output}")
        lines.append(f"Total tokens: {total_prompt + total_output}")
    else:
        lines.append(f"Estimated prompt tokens: {total_prompt}")
        lines.append(f"Estimated output tokens: {total_output}")
        lines.append(f"Estimated total tokens: {total_prompt + total_output}")
    lines.extend(["", "## Per Model", ""])
    by_model: dict[str, list[TelemetryEntry]] = {}
    for entry in entries:
        key = entry.model or entry.agent_id or entry.stage_type
        by_model.setdefault(key, []).append(entry)
    if not by_model:
        lines.append("- None")
    for model, model_entries in sorted(by_model.items()):
        successes = sum(1 for entry in model_entries if entry.status == "pass")
        token_total = sum(entry.prompt_tokens + entry.output_tokens for entry in model_entries)
        model_actual = all(entry.actual_prompt_tokens is not None for entry in model_entries)
        token_label = "tokens" if model_actual else "estimated tokens"
        lines.append(
            f"- `{model}`: stages={len(model_entries)}, successes={successes}, "
            f"failures={len(model_entries) - successes}, "
            f"runtime={sum(entry.duration_seconds for entry in model_entries):.3f}s, "
            f"{token_label}={token_total}"
        )
    lines.extend(["", "## Stages", ""])
    for entry in entries:
        if entry.actual_prompt_tokens is not None and entry.actual_output_tokens is not None:
            token_str = f"actual_tokens={entry.actual_prompt_tokens}+{entry.actual_output_tokens}"
        else:
            token_str = f"estimated_tokens={entry.prompt_tokens + entry.output_tokens}"
        lines.append(
            f"- `{entry.stage_id}` ({entry.stage_type}): {entry.status}, "
            f"agent={entry.agent_id or ''}, model={entry.model or ''}, "
            f"retry={entry.retry_count}, runtime={entry.duration_seconds:.3f}s, "
            f"{token_str}"
        )
    lines.append("")
    return "\n".join(lines)


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:\s*`?([^`\n]+)`?", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _float_field(text: str, name: str) -> float:
    value = _field(text, name)
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def _int_field(text: str, name: str) -> int | None:
    value = _field(text, name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*\n\n(?:```[A-Za-z0-9_-]*\n)?(.*?)(?:\n```)?(?:\n\n^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""
