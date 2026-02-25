from pathlib import Path

from PIL import Image

from comicstrip_tutor.composition.strip_composer import compose_strip
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def test_strip_composition_creates_png(tmp_path: Path) -> None:
    panel_paths: list[str] = []
    for idx in range(1, 5):
        path = tmp_path / f"panel_{idx}.png"
        Image.new("RGB", (256, 256), color=(240, 240, 240)).save(path)
        panel_paths.append(str(path))
    storyboard = Storyboard(
        topic="topic",
        story_title="story",
        character_style_guide="guide",
        recurring_characters=["Ada", "Turing"],
        panels=[
            PanelScript(
                panel_number=i,
                scene_description="Valid scene description text",
                dialogue_or_caption="Caption text for readability check",
                teaching_intent="teach intent",
            )
            for i in range(1, 5)
        ],
        recap_panel=4,
    )
    out_png = tmp_path / "strip.png"
    compose_strip(storyboard=storyboard, panel_image_paths=panel_paths, output_png=out_png)
    assert out_png.exists()
