"""Per-run quality report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from comicstrip_tutor.storage.io_utils import read_json, write_text


def _format_issue_rows(critique_payload: dict[str, Any]) -> list[str]:
    rows = [
        "| Reviewer | Severity | Code | Panel | Message | Recommendation |",
        "|---|---|---|---:|---|---|",
    ]
    issue_count = 0
    for reviewer in critique_payload.get("reviewer_reports", []):
        reviewer_name = str(reviewer.get("reviewer", "unknown"))
        for issue in reviewer.get("issues", []):
            issue_count += 1
            panel_number = issue.get("panel_number")
            panel_text = str(panel_number) if panel_number is not None else "-"
            rows.append(
                "| "
                f"{reviewer_name} | {issue.get('severity', 'n/a')} | "
                f"{issue.get('issue_code', 'n/a')} | {panel_text} | "
                f"{str(issue.get('message', '')).replace('|', '/')} | "
                f"{str(issue.get('recommendation', '')).replace('|', '/')} |"
            )
            if issue_count >= 20:
                rows.append("| ... | ... | ... | ... | Truncated after 20 issues | ... |")
                return rows
    if issue_count == 0:
        rows.append("| none | - | - | - | No critique issues detected. | - |")
    return rows


def write_quality_report(
    *,
    output_path: Path,
    run_id: str,
    model_key: str,
    manifest_payload: dict[str, Any],
    critique_payload: dict[str, Any] | None,
    evaluation_payload: dict[str, Any] | None,
) -> Path:
    """Write a markdown quality report for a run/model."""
    completion_status = str(manifest_payload.get("completion_status", "unknown"))
    lines = [
        f"# Run Quality Report: {run_id} / {model_key}",
        "",
        "## Run status",
        f"- completion_status: `{completion_status}`",
        f"- estimated_cost_usd: `{manifest_payload.get('total_estimated_cost_usd', 0.0)}`",
    ]
    error_type = manifest_payload.get("error_type")
    error_message = manifest_payload.get("error_message")
    if error_type:
        lines.append(f"- error_type: `{error_type}`")
    if error_message:
        lines.append(f"- error_message: `{error_message}`")

    if evaluation_payload is not None:
        lines.extend(
            [
                "",
                "## Learning quality",
                f"- LES: `{evaluation_payload.get('learning_effectiveness_score')}`",
                f"- comprehension_score: `{evaluation_payload.get('comprehension_score')}`",
                f"- technical_rigor_score: `{evaluation_payload.get('technical_rigor_score')}`",
                f"- publishable: `{evaluation_payload.get('publishable')}`",
            ]
        )
        publishable_reasons = evaluation_payload.get("publishable_reasons", [])
        if publishable_reasons:
            lines.append("- publishable_reasons:")
            for reason in publishable_reasons:
                lines.append(f"  - {reason}")

    if critique_payload is not None:
        lines.extend(
            [
                "",
                "## Critique summary",
                f"- overall_score: `{critique_payload.get('overall_score')}`",
                f"- blocking_issue_count: `{critique_payload.get('blocking_issue_count')}`",
                f"- major_issue_count: `{critique_payload.get('major_issue_count')}`",
                f"- rewrite_count: `{critique_payload.get('rewrite_count', 0)}`",
                "",
                "## Critique issues",
            ]
        )
        lines.extend(_format_issue_rows(critique_payload))
        recommended_actions = critique_payload.get("recommended_actions", [])
        if recommended_actions:
            lines.extend(["", "## Recommended actions"])
            for action in recommended_actions:
                lines.append(f"- {action}")

    write_text(output_path, "\n".join(lines) + "\n")
    return output_path


def generate_quality_report_from_run(*, run_root: Path, model_key: str) -> Path:
    """Generate quality report from saved run artifacts."""
    run_id = run_root.name
    manifest_payload = read_json(run_root / f"manifest_{model_key}.json")
    critique_path = run_root / "critique" / f"pre_render_{model_key}.json"
    critique_payload = read_json(critique_path) if critique_path.exists() else None
    eval_path = run_root / "evaluation" / f"{model_key}.json"
    evaluation_payload = read_json(eval_path) if eval_path.exists() else None
    output_path = run_root / "reports" / f"quality_{model_key}.md"
    return write_quality_report(
        output_path=output_path,
        run_id=run_id,
        model_key=model_key,
        manifest_payload=manifest_payload,
        critique_payload=critique_payload,
        evaluation_payload=evaluation_payload,
    )
