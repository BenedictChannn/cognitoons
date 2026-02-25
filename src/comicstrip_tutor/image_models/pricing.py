"""Rough per-image cost estimates for model comparison."""

from __future__ import annotations

MODEL_ESTIMATED_COST_USD: dict[str, float] = {
    "gpt-image-1-mini": 0.01,
    "gpt-image-1": 0.03,
    "gpt-image-1.5": 0.08,
    "gemini-2.5-flash-image": 0.012,
    "gemini-3-pro-image-preview": 0.07,
}


def estimate_cost(model_key: str, panel_count: int) -> float:
    """Estimate render cost for model and panel count."""
    unit_cost = MODEL_ESTIMATED_COST_USD.get(model_key, 0.02)
    return round(unit_cost * panel_count, 4)
