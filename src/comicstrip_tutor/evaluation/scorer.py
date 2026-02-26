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


def _technical_rigor_from_critique(critique_report: CritiqueReport | None) -> float | None:
    if critique_report is None:
        return None
    technical = next(
        (report for report in critique_report.reviewer_reports if report.reviewer == "technical"),
        None,
    )
    if technical is None:
        return None
    score = 1.0
    for issue in technical.issues:
        if issue.issue_code == "technical_key_point_missing":
            score -= 0.2
        elif issue.issue_code == "technical_rigor_low":
            score -= 0.1
        elif issue.issue_code == "technical_misconception_unaddressed":
            score -= 0.03
    if any(issue.severity == "critical" for issue in technical.issues):
        score = min(score, 0.74)
    return round(max(0.0, score), 4)


def _publishability(
    *,
    checks: dict[str, bool],
    comprehension_score: float | None,
    technical_rigor_score: float | None,
    learning_effectiveness_score: float | None,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    required_checks = ("panel_count_valid", "captions_non_empty", "images_exist", "recap_present")
    for check_name in required_checks:
        if not checks.get(check_name, False):
            reasons.append(f"Structural check failed: {check_name}")
    if learning_effectiveness_score is None or learning_effectiveness_score < 0.80:
        reasons.append("LES below threshold (0.80).")
    if comprehension_score is None or comprehension_score < 0.80:
        reasons.append("Comprehension score below threshold (0.80).")
    if technical_rigor_score is None or technical_rigor_score < 0.95:
        reasons.append("Technical rigor score below threshold (0.95).")
    return (len(reasons) == 0), reasons


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
    technical_rigor_score = _technical_rigor_from_critique(critique_report)
    learning_effectiveness_score = _learning_effectiveness(
        comprehension_score=comprehension_score,
        technical_rigor_score=technical_rigor_score,
        readability_score=metrics.readability,
        coherence_score=metrics.coherence,
    )
    publishable, publishable_reasons = _publishability(
        checks=checks,
        comprehension_score=comprehension_score,
        technical_rigor_score=technical_rigor_score,
        learning_effectiveness_score=learning_effectiveness_score,
    )
    return EvaluationResult(
        run_id=run_id,
        model_key=model_key,
        metrics=metrics,
        comprehension_score=comprehension_score,
        technical_rigor_score=technical_rigor_score,
        learning_effectiveness_score=learning_effectiveness_score,
        publishable=publishable,
        publishable_reasons=publishable_reasons,
        checks=checks,
        notes=[
            f"aggregate={metrics.aggregate}",
            f"les={learning_effectiveness_score}",
        ],
    )
