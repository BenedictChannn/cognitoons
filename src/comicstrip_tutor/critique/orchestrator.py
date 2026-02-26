"""Critique orchestrator and gating logic."""

from __future__ import annotations

from comicstrip_tutor.critique.reviewers import (
    CritiqueContext,
    beginner_reviewer,
    first_year_reviewer,
    pedagogy_reviewer,
    technical_reviewer,
    visual_reviewer,
)
from comicstrip_tutor.schemas.critique import CritiqueIssue, CritiqueReport, ReviewerCritique
from comicstrip_tutor.schemas.runs import CritiqueMode
from comicstrip_tutor.schemas.storyboard import Storyboard


def _collect_actions(issues: list[CritiqueIssue]) -> list[str]:
    actions: list[str] = []
    for issue in issues:
        if issue.severity in {"critical", "major"}:
            actions.append(issue.recommendation)
    # preserve order while deduplicating
    return list(dict.fromkeys(actions))


def run_storyboard_critique(
    *,
    run_id: str,
    stage: str,
    critique_mode: CritiqueMode,
    storyboard: Storyboard,
    expected_key_points: list[str],
    misconceptions: list[str],
    audience_level: str,
) -> CritiqueReport:
    """Run full critique panel on a storyboard."""
    if critique_mode == "off":
        return CritiqueReport(
            run_id=run_id,
            stage=stage,
            critique_mode=critique_mode,
            overall_verdict="pass",
            overall_score=1.0,
            reviewer_reports=[],
            recommended_actions=[],
        )

    context = CritiqueContext(
        expected_key_points=expected_key_points,
        misconceptions=misconceptions,
        audience_level=audience_level,
    )
    reviewers: list[ReviewerCritique] = [
        technical_reviewer(storyboard, context),
        beginner_reviewer(storyboard, context),
        first_year_reviewer(storyboard, context),
        pedagogy_reviewer(storyboard, context),
        visual_reviewer(storyboard, context),
    ]
    all_issues = [issue for reviewer in reviewers for issue in reviewer.issues]
    blocking_count = sum(issue.severity == "critical" for issue in all_issues)
    major_count = sum(issue.severity == "major" for issue in all_issues)
    overall_score = round(sum(reviewer.score for reviewer in reviewers) / len(reviewers), 4)
    verdict = "fail" if blocking_count > 0 else "pass"
    return CritiqueReport(
        run_id=run_id,
        stage=stage,
        critique_mode=critique_mode,
        overall_verdict=verdict,
        overall_score=overall_score,
        blocking_issue_count=blocking_count,
        major_issue_count=major_count,
        reviewer_reports=reviewers,
        recommended_actions=_collect_actions(all_issues),
    )


def should_block_render(critique_report: CritiqueReport) -> bool:
    """Determine if strict mode should block rendering."""
    if critique_report.critique_mode != "strict":
        return False
    if critique_report.blocking_issue_count > 0:
        return True
    return critique_report.major_issue_count > 2


def needs_rewrite(critique_report: CritiqueReport) -> bool:
    """Determine if report requires rewrite cycle."""
    return critique_report.blocking_issue_count > 0 or critique_report.major_issue_count > 2
