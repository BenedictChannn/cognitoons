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
from comicstrip_tutor.schemas.critique import CritiqueReport
from comicstrip_tutor.schemas.evaluation import EvaluationMetricSet, EvaluationResult
from comicstrip_tutor.schemas.storyboard import Storyboard


def _reviewer_score(critique_report: CritiqueReport | None, reviewer: str) -> float | None:
    if critique_report is None:
        return None
    for report in critique_report.reviewer_reports:
        if report.reviewer == reviewer:
            return report.score
    return None


def _learning_effectiveness(
    *,
    comprehension_score: float | None,
    technical_rigor_score: float | None,
    readability_score: float,
    coherence_score: float,
) -> float | None:
    if comprehension_score is None or technical_rigor_score is None:
        return None
    value = (
        0.35 * comprehension_score
        + 0.35 * technical_rigor_score
        + 0.15 * readability_score
        + 0.15 * coherence_score
    )
    return round(value, 4)


def score_render_run(
    *,
    run_id: str,
    model_key: str,
    storyboard: Storyboard,
    expected_key_points: list[str],
    prompt_paths: list[Path],
    image_paths: list[Path],
    enable_llm_judge: bool = False,
    critique_report: CritiqueReport | None = None,
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
    beginner_score = _reviewer_score(critique_report, "beginner")
    first_year_score = _reviewer_score(critique_report, "first_year")
    comprehension_score = None
    if beginner_score is not None and first_year_score is not None:
        comprehension_score = round((beginner_score + first_year_score) / 2.0, 4)
    technical_rigor_score = _reviewer_score(critique_report, "technical")
    learning_effectiveness_score = _learning_effectiveness(
        comprehension_score=comprehension_score,
        technical_rigor_score=technical_rigor_score,
        readability_score=metrics.readability,
        coherence_score=metrics.coherence,
    )
    return EvaluationResult(
        run_id=run_id,
        model_key=model_key,
        metrics=metrics,
        comprehension_score=comprehension_score,
        technical_rigor_score=technical_rigor_score,
        learning_effectiveness_score=learning_effectiveness_score,
        checks=checks,
        notes=[
            f"aggregate={metrics.aggregate}",
            f"les={learning_effectiveness_score}",
        ],
    )
