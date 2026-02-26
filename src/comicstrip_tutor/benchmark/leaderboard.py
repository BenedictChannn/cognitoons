"""Leaderboard aggregation."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from comicstrip_tutor.schemas.benchmark import BenchmarkModelResult


def _top_reasons(reasons: Iterable[str], limit: int = 3) -> str:
    counts: dict[str, int] = {}
    for reason in reasons:
        if not reason:
            continue
        counts[reason] = counts.get(reason, 0) + 1
    if not counts:
        return "none"
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    return "; ".join(f"{reason} ({count})" for reason, count in ranked)


def build_leaderboard(results: list[BenchmarkModelResult]) -> list[dict[str, float | str]]:
    """Aggregate benchmark model results."""
    grouped_scores: dict[str, list[float]] = defaultdict(list)
    grouped_costs: dict[str, list[float]] = defaultdict(list)
    grouped_les: dict[str, list[float]] = defaultdict(list)
    grouped_comprehension: dict[str, list[float]] = defaultdict(list)
    grouped_rigor: dict[str, list[float]] = defaultdict(list)
    grouped_publishable: dict[str, list[bool]] = defaultdict(list)
    grouped_failure_reasons: dict[str, list[str]] = defaultdict(list)
    for result in results:
        grouped_scores[result.model_key].append(result.score)
        grouped_costs[result.model_key].append(result.cost_usd)
        if result.learning_effectiveness_score is not None:
            grouped_les[result.model_key].append(result.learning_effectiveness_score)
        if result.comprehension_score is not None:
            grouped_comprehension[result.model_key].append(result.comprehension_score)
        if result.technical_rigor_score is not None:
            grouped_rigor[result.model_key].append(result.technical_rigor_score)
        grouped_publishable[result.model_key].append(result.publishable)
        if not result.publishable:
            grouped_failure_reasons[result.model_key].extend(result.publishable_reasons)
    leaderboard: list[dict[str, float | str]] = []
    for model_key, scores in grouped_scores.items():
        les_values = grouped_les.get(model_key, [])
        comprehension_values = grouped_comprehension.get(model_key, [])
        rigor_values = grouped_rigor.get(model_key, [])
        publishable_values = grouped_publishable.get(model_key, [])
        mean_score = round(sum(scores) / len(scores), 4)
        mean_les = round(sum(les_values) / len(les_values), 4) if les_values else mean_score
        leaderboard.append(
            {
                "model_key": model_key,
                "mean_score": mean_score,
                "mean_les": mean_les,
                "mean_comprehension": (
                    round(sum(comprehension_values) / len(comprehension_values), 4)
                    if comprehension_values
                    else 0.0
                ),
                "mean_rigor": (
                    round(sum(rigor_values) / len(rigor_values), 4) if rigor_values else 0.0
                ),
                "publish_gate_pass_rate": (
                    round(
                        sum(1 for value in publishable_values if value) / len(publishable_values),
                        4,
                    )
                    if publishable_values
                    else 0.0
                ),
                "top_gate_failures": _top_reasons(grouped_failure_reasons.get(model_key, [])),
                "total_cost_usd": round(sum(grouped_costs[model_key]), 4),
            }
        )
    leaderboard.sort(
        key=lambda row: (float(row["mean_les"]), float(row["mean_score"])),
        reverse=True,
    )
    return leaderboard
