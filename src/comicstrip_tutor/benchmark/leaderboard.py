"""Leaderboard aggregation."""

from __future__ import annotations

from collections import defaultdict

from comicstrip_tutor.schemas.benchmark import BenchmarkModelResult


def build_leaderboard(results: list[BenchmarkModelResult]) -> list[dict[str, float | str]]:
    """Aggregate benchmark model results."""
    grouped_scores: dict[str, list[float]] = defaultdict(list)
    grouped_costs: dict[str, list[float]] = defaultdict(list)
    for result in results:
        grouped_scores[result.model_key].append(result.score)
        grouped_costs[result.model_key].append(result.cost_usd)
    leaderboard: list[dict[str, float | str]] = []
    for model_key, scores in grouped_scores.items():
        leaderboard.append(
            {
                "model_key": model_key,
                "mean_score": round(sum(scores) / len(scores), 4),
                "total_cost_usd": round(sum(grouped_costs[model_key]), 4),
            }
        )
    leaderboard.sort(key=lambda row: row["mean_score"], reverse=True)
    return leaderboard
