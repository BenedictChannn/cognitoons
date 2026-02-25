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
        "| Rank | Model | Mean Score | Total Cost (USD) |",
        "|---:|---|---:|---:|",
    ]
    for idx, row in enumerate(leaderboard, start=1):
        model_key = str(row["model_key"])
        mean_score = float(row["mean_score"])
        total_cost_usd = float(row["total_cost_usd"])
        lines.append(f"| {idx} | {model_key} | {mean_score:.4f} | {total_cost_usd:.4f} |")
    write_text(output_path, "\n".join(lines) + "\n")
