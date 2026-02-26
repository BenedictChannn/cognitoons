"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

from comicstrip_tutor.storage.io_utils import write_text


def write_markdown_leaderboard(
    *,
    output_path: Path,
    benchmark_id: str,
    leaderboard: list[dict[str, float | str]],
) -> None:
    """Write markdown leaderboard report."""
    lines = [
        f"# ComicStrip Tutor Benchmark Report ({benchmark_id})",
        "",
        (
            "| Rank | Model | Mean LES | Mean Score | Mean Compr. | "
            "Mean Rigor | Publish Gate Pass | Top Gate Failures | Total Cost (USD) |"
        ),
        "|---:|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for idx, row in enumerate(leaderboard, start=1):
        model_key = str(row["model_key"])
        mean_les = float(row.get("mean_les", row["mean_score"]))
        mean_score = float(row["mean_score"])
        mean_comprehension = float(row.get("mean_comprehension", 0.0))
        mean_rigor = float(row.get("mean_rigor", 0.0))
        publish_gate_pass_rate = float(row.get("publish_gate_pass_rate", 0.0))
        top_gate_failures = str(row.get("top_gate_failures", "none"))
        total_cost_usd = float(row["total_cost_usd"])
        lines.append(
            "| "
            f"{idx} | {model_key} | {mean_les:.4f} | {mean_score:.4f} | "
            f"{mean_comprehension:.4f} | {mean_rigor:.4f} | "
            f"{publish_gate_pass_rate:.4f} | {top_gate_failures} | {total_cost_usd:.4f} |"
        )
    write_text(output_path, "\n".join(lines) + "\n")
