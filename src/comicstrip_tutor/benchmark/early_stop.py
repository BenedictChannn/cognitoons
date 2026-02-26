"""Early stopping logic for weak models."""

from __future__ import annotations


def should_early_stop(
    *,
    model_scores: list[float],
    best_mean_so_far: float,
    min_samples: int = 3,
    weak_gap: float = 0.25,
) -> bool:
    """Stop if model is clearly weak against current best."""
    if len(model_scores) < min_samples:
        return False
    mean_score = sum(model_scores) / len(model_scores)
    return (best_mean_so_far - mean_score) >= weak_gap
