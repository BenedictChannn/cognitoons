import pytest
from pydantic import ValidationError

from comicstrip_tutor.schemas.planning import LearningPlan
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def test_learning_plan_requires_objective() -> None:
    with pytest.raises(ValidationError):
        LearningPlan(topic="x", objectives=[], recap_message="ok")


def test_storyboard_requires_two_characters() -> None:
    panels = [
        PanelScript(
            panel_number=i,
            scene_description="A long-enough scene description",
            dialogue_or_caption="Useful caption text",
            teaching_intent="Teach a thing",
        )
        for i in range(1, 5)
    ]
    with pytest.raises(ValidationError):
        Storyboard(
            topic="T",
            story_title="S",
            character_style_guide="Guide",
            recurring_characters=["Ada"],
            panels=panels,
            recap_panel=4,
        )
