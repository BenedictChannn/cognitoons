from pathlib import Path

from PIL import Image

from comicstrip_tutor.evaluation.scorer import score_render_run
from comicstrip_tutor.schemas.critique import CritiqueReport, ReviewerCritique
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def _storyboard() -> Storyboard:
    return Storyboard(
        topic="UCT",
        story_title="UCT comic",
        character_style_guide="clean style",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=i,
                scene_description="confusion scene where a naive choice fails",
                dialogue_or_caption="We balance exploration and exploitation.",
                teaching_intent="Teach exploration and value estimate tradeoff.",
            )
            for i in range(1, 5)
        ],
        recap_panel=4,
    )


def test_learning_effectiveness_score_is_computed(tmp_path: Path) -> None:
    storyboard = _storyboard()
    prompt_paths: list[Path] = []
    image_paths: list[Path] = []
    for idx in range(1, 5):
        prompt = tmp_path / f"panel_{idx}.txt"
        prompt.write_text("prompt", encoding="utf-8")
        prompt_paths.append(prompt)
        image = tmp_path / f"panel_{idx}.png"
        Image.new("RGB", (64, 64)).save(image)
        image_paths.append(image)

    critique = CritiqueReport(
        run_id="run",
        stage="pre_render:model",
        critique_mode="warn",
        overall_verdict="pass",
        overall_score=0.82,
        reviewer_reports=[
            ReviewerCritique(
                reviewer="beginner",
                verdict="pass",
                score=0.8,
                confidence=0.7,
                summary="ok",
            ),
            ReviewerCritique(
                reviewer="first_year",
                verdict="pass",
                score=0.84,
                confidence=0.7,
                summary="ok",
            ),
            ReviewerCritique(
                reviewer="technical",
                verdict="pass",
                score=0.9,
                confidence=0.8,
                summary="ok",
            ),
        ],
    )

    result = score_render_run(
        run_id="run",
        model_key="gpt-image-1-mini",
        storyboard=storyboard,
        expected_key_points=["exploration vs exploitation"],
        prompt_paths=prompt_paths,
        image_paths=image_paths,
        critique_report=critique,
    )
    assert result.learning_effectiveness_score is not None
    assert result.comprehension_score is not None
    assert result.technical_rigor_score is not None
