from comicstrip_tutor.pipeline.panel_prompt_builder import build_panel_prompt
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def test_prompt_includes_style_guide_and_characters() -> None:
    storyboard = Storyboard(
        topic="UCT",
        story_title="UCT comic",
        character_style_guide="Consistent style guide",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=1,
                scene_description="Ada at whiteboard describing trees and choices",
                dialogue_or_caption="Exploration versus exploitation matters.",
                teaching_intent="Introduce core tradeoff",
            )
        ]
        * 4,
        recap_panel=4,
    )
    prompt = build_panel_prompt(storyboard, storyboard.panels[0])
    assert "Consistent style guide" in prompt
    assert "Ada, Turing" in prompt
