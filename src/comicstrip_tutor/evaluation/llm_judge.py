"""Optional cheap LLM-judge scorer."""

from __future__ import annotations

from comicstrip_tutor.schemas.storyboard import Storyboard


def cheap_llm_judge(
    storyboard: Storyboard,
    expected_key_points: list[str],
    enabled: bool,
) -> float | None:
    """Lightweight stand-in judge (cheap by default)."""
    if not enabled:
        return None
    score = 0.55
    score += 0.15 if len(storyboard.panels) >= 6 else 0.0
    if expected_key_points:
        score += min(0.25, 0.05 * len(expected_key_points))
    return round(min(1.0, score), 4)
