from comicstrip_tutor.critique.rewrite import apply_targeted_rewrites
from comicstrip_tutor.schemas.critique import CritiqueIssue, CritiqueReport, ReviewerCritique
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def _storyboard() -> Storyboard:
    return Storyboard(
        topic="UCT",
        story_title="UCT",
        character_style_guide="clean",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=1,
                scene_description="setup scene",
                dialogue_or_caption="Intro caption",
                teaching_intent="Teach base idea.",
                expected_takeaway="Understand base idea.",
            ),
            PanelScript(
                panel_number=2,
                scene_description="insight scene",
                dialogue_or_caption=(
                    "Dense caption with many many many words to force rewrite behavior."
                ),
                teaching_intent="Teach step two.",
                expected_takeaway="Understand step two.",
            ),
            PanelScript(
                panel_number=3,
                scene_description="insight scene",
                dialogue_or_caption="Another caption",
                teaching_intent="Teach step three.",
                expected_takeaway="Understand step three.",
            ),
            PanelScript(
                panel_number=4,
                scene_description="recap scene",
                dialogue_or_caption="Recap",
                teaching_intent="Recap",
                expected_takeaway="Recap understanding.",
            ),
        ],
        recap_panel=2,
    )


def test_rewrite_uses_issue_code_not_message_text() -> None:
    storyboard = _storyboard()
    report = CritiqueReport(
        run_id="run",
        stage="post_planning",
        critique_mode="strict",
        overall_verdict="fail",
        overall_score=0.2,
        blocking_issue_count=1,
        major_issue_count=1,
        reviewer_reports=[
            ReviewerCritique(
                reviewer="technical",
                verdict="fail",
                score=0.1,
                confidence=0.9,
                summary="",
                issues=[
                    CritiqueIssue(
                        reviewer="technical",
                        severity="critical",
                        issue_code="technical_key_point_missing",
                        message="Custom wording without canonical phrase",
                        recommendation="",
                        metadata={"missing_key_point": "upper confidence bound"},
                    ),
                    CritiqueIssue(
                        reviewer="technical",
                        severity="major",
                        issue_code="technical_misconception_unaddressed",
                        message="Another custom phrasing",
                        recommendation="",
                    ),
                ],
            )
        ],
    )

    rewritten, notes = apply_targeted_rewrites(
        storyboard=storyboard,
        critique_report=report,
        expected_key_points=["exploration"],
        misconceptions=["greedy always wins", "explore randomly forever"],
    )

    assert rewritten.recap_panel == len(rewritten.panels)
    assert "upper confidence bound" in rewritten.panels[2].teaching_intent.lower()
    assert rewritten.panels[0].misconception_addressed is not None
    assert any("Injected missing key point" in note for note in notes)
