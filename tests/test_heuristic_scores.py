from pathlib import Path

from PIL import Image

from comicstrip_tutor.evaluation.heuristics import concept_coverage, heuristic_checks
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def _storyboard() -> Storyboard:
    return Storyboard(
        topic="UCT",
        story_title="story",
        character_style_guide="consistent art style",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=i,
                scene_description="Ada and Turing discuss choices in a tree diagram scene",
                dialogue_or_caption="Exploration and exploitation are both needed in UCT.",
                teaching_intent="exploration vs exploitation and visit counts",
            )
            for i in range(1, 5)
        ],
        recap_panel=4,
    )


def test_concept_coverage_positive() -> None:
    score = concept_coverage(_storyboard(), ["exploration vs exploitation", "visit counts"])
    assert score > 0.5


def test_heuristic_checks_image_exists(tmp_path: Path) -> None:
    storyboard = _storyboard()
    image_paths = []
    for i in range(4):
        image_path = tmp_path / f"panel_{i}.png"
        Image.new("RGB", (10, 10)).save(image_path)
        image_paths.append(image_path)
    checks = heuristic_checks(storyboard, image_paths)
    assert checks["images_exist"]
