"""Experiment trend reporting from registry events."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from comicstrip_tutor.storage.io_utils import write_text


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def write_trend_report(*, registry_path: Path, output_path: Path) -> Path:
    """Generate markdown trend report from registry JSONL events."""
    events = _read_jsonl(registry_path)
    render_complete = [event for event in events if event.get("event") == "render_complete"]
    render_failed = [event for event in events if event.get("event") == "render_failed"]
    feedback_events = [event for event in events if event.get("event") == "user_feedback"]

    model_scores: dict[str, list[float]] = defaultdict(list)
    model_costs: dict[str, list[float]] = defaultdict(list)
    for event in render_complete:
        model = str(event.get("model", "unknown"))
        score = event.get("aggregate_score")
        cost = event.get("estimated_cost_usd")
        if isinstance(score, (int, float)):
            model_scores[model].append(float(score))
        if isinstance(cost, (int, float)):
            model_costs[model].append(float(cost))

    failure_types: dict[str, int] = defaultdict(int)
    for event in render_failed:
        failure_types[str(event.get("error_type", "unknown"))] += 1

    feedback_by_model: dict[str, list[float]] = defaultdict(list)
    for event in feedback_events:
        model = str(event.get("model", "unknown"))
        rating = event.get("rating")
        if isinstance(rating, (int, float)):
            feedback_by_model[model].append(float(rating))

    lines = [
        "# Experiment Trend Report",
        "",
        "## Event summary",
        f"- total_events: `{len(events)}`",
        f"- render_complete: `{len(render_complete)}`",
        f"- render_failed: `{len(render_failed)}`",
        f"- user_feedback_events: `{len(feedback_events)}`",
        "",
        "## Model performance trend",
        "| Model | Avg Aggregate Score | Avg Cost (USD) | Render Count |",
        "|---|---:|---:|---:|",
    ]
    for model in sorted(model_scores):
        scores = model_scores[model]
        costs = model_costs.get(model, [])
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_cost = sum(costs) / len(costs) if costs else 0.0
        lines.append(f"| {model} | {avg_score:.4f} | {avg_cost:.4f} | {len(scores)} |")
    if not model_scores:
        lines.append("| none | 0.0000 | 0.0000 | 0 |")

    lines.extend(
        [
            "",
            "## Failure taxonomy trend",
            "| Error Type | Count |",
            "|---|---:|",
        ]
    )
    if failure_types:
        for error_type, count in sorted(
            failure_types.items(), key=lambda item: item[1], reverse=True
        ):
            lines.append(f"| {error_type} | {count} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Feedback trend",
            "| Model | Avg Rating | Feedback Count |",
            "|---|---:|---:|",
        ]
    )
    if feedback_by_model:
        for model in sorted(feedback_by_model):
            ratings = feedback_by_model[model]
            avg_rating = sum(ratings) / len(ratings)
            lines.append(f"| {model} | {avg_rating:.2f} | {len(ratings)} |")
    else:
        lines.append("| none | 0.00 | 0 |")

    write_text(output_path, "\n".join(lines) + "\n")
    return output_path
