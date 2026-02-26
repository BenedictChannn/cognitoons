from comicstrip_tutor.critique.orchestrator import run_storyboard_critique, should_block_render
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def _sample_storyboard() -> Storyboard:
    return Storyboard(
        topic="UCT",
        story_title="UCT intro",
        character_style_guide="clean style",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=1,
                scene_description="setup scene where confusion starts",
                dialogue_or_caption="We need to balance exploration and exploitation.",
                teaching_intent="Teach exploration versus exploitation tradeoff.",
                misconception_addressed="Always choose highest average reward.",
                expected_takeaway="Tradeoff exists.",
            ),
            PanelScript(
                panel_number=2,
                scene_description="confusion scene with naive policy failing",
                dialogue_or_caption="A naive greedy move can miss better long-term value.",
                teaching_intent="Teach why naive greed fails.",
                metaphor_anchor="Hallways in a maze",
                misconception_addressed="Greedy choice is always best.",
                expected_takeaway="Need uncertainty bonus.",
            ),
            PanelScript(
                panel_number=3,
                scene_description="insight scene introducing confidence estimates",
                dialogue_or_caption="Add a confidence bonus based on visit counts.",
                teaching_intent="Teach UCT confidence adjustment.",
                misconception_addressed="No need to revisit uncertain branches.",
                expected_takeaway="UCT uses value plus uncertainty.",
            ),
            PanelScript(
                panel_number=4,
                scene_description="recap scene summarizing the final idea",
                dialogue_or_caption="UCT balances value estimate and uncertainty over time.",
                teaching_intent="Recap UCT decision rule and tradeoff.",
                misconception_addressed="UCT is random guessing.",
                expected_takeaway="UCT balances exploration and exploitation.",
            ),
        ],
        recap_panel=4,
    )


def test_critique_warn_mode_returns_report() -> None:
    report = run_storyboard_critique(
        run_id="test",
        stage="post_planning",
        critique_mode="warn",
        storyboard=_sample_storyboard(),
        expected_key_points=["exploration vs exploitation", "visit counts"],
        misconceptions=["always choose highest average reward"],
        audience_level="beginner",
    )
    assert report.reviewer_reports
    assert report.overall_score > 0


def test_critique_strict_blocks_when_critical_issue_exists() -> None:
    broken = _sample_storyboard()
    broken.recap_panel = 2
    report = run_storyboard_critique(
        run_id="test",
        stage="post_planning",
        critique_mode="strict",
        storyboard=broken,
        expected_key_points=["exploration vs exploitation"],
        misconceptions=[],
        audience_level="beginner",
    )
    assert report.blocking_issue_count >= 1
    assert should_block_render(report)
