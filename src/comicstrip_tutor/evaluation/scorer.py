"""Evaluation scorer entrypoint."""

from __future__ import annotations

from pathlib import Path

from comicstrip_tutor.evaluation.heuristics import (
    coherence,
    concept_coverage,
    consistency,
    heuristic_checks,
    readability,
    visual_text_alignment,
)
from comicstrip_tutor.evaluation.llm_judge import cheap_llm_judge
from comicstrip_tutor.schemas.evaluation import EvaluationMetricSet, EvaluationResult
from comicstrip_tutor.schemas.storyboard import Storyboard


def score_render_run(
    *,
    run_id: str,
    model_key: str,
    storyboard: Storyboard,
    expected_key_points: list[str],
    prompt_paths: list[Path],
    image_paths: list[Path],
    enable_llm_judge: bool = False,
) -> EvaluationResult:
    """Compute rubric + checks for render run."""
    metrics = EvaluationMetricSet(
        concept_coverage=concept_coverage(storyboard, expected_key_points),
        coherence=coherence(storyboard),
        visual_text_alignment=visual_text_alignment(storyboard),
        readability=readability(storyboard),
        consistency=consistency(storyboard, prompt_paths),
        llm_judge=cheap_llm_judge(storyboard, expected_key_points, enable_llm_judge),
    )
    checks = heuristic_checks(storyboard, image_paths)
    return EvaluationResult(
        run_id=run_id,
        model_key=model_key,
        metrics=metrics,
        checks=checks,
        notes=[f"aggregate={metrics.aggregate}"],
    )
