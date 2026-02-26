"""Single-panel reroll pipeline."""

from __future__ import annotations

from pydantic import TypeAdapter

from comicstrip_tutor.composition.strip_composer import compose_strip
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.base import PanelImageRequest
from comicstrip_tutor.image_models.registry import create_model
from comicstrip_tutor.pipeline.panel_prompt_builder import build_panel_prompt
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.schemas.storyboard import Storyboard
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import read_json, write_json, write_text

_STORYBOARD_ADAPTER = TypeAdapter(Storyboard)
_RUN_CONFIG_ADAPTER = TypeAdapter(RunConfig)


def reroll_single_panel(
    *,
    run_id: str,
    model_key: str,
    panel_number: int,
    metaphor: str | None,
    mode: str,
    dry_run: bool,
    app_config: AppConfig,
) -> str:
    """Regenerate exactly one panel and recomposite strip."""
    store = ArtifactStore(app_config.output_root)
    paths = store.open_run(run_id)
    storyboard = _STORYBOARD_ADAPTER.validate_python(read_json(paths.root / "storyboard.json"))
    run_config = _RUN_CONFIG_ADAPTER.validate_python(read_json(paths.root / "run_config.json"))
    target_panel = next(panel for panel in storyboard.panels if panel.panel_number == panel_number)
    if metaphor:
        target_panel.metaphor_anchor = metaphor
        write_json(paths.root / "storyboard.json", storyboard.model_dump())
    prompt = build_panel_prompt(
        storyboard,
        target_panel,
        image_text_mode=run_config.image_text_mode,
    )
    prompt_path = paths.prompts_dir / f"panel_{panel_number:02d}.txt"
    write_text(prompt_path, prompt + "\n")

    model = create_model(model_key, app_config)
    size = (1024, 1024) if mode == "publish" else (768, 768)
    image_dir = paths.images_dir / model_key
    image_dir.mkdir(parents=True, exist_ok=True)
    output_path = image_dir / f"panel_{panel_number:02d}.png"
    model.generate_panel_image(
        PanelImageRequest(
            panel_number=panel_number,
            prompt=prompt,
            width=size[0],
            height=size[1],
            style_guide=storyboard.character_style_guide,
            output_path=str(output_path),
            dry_run=dry_run,
        )
    )
    panel_paths = [
        str(image_dir / f"panel_{panel.panel_number:02d}.png") for panel in storyboard.panels
    ]
    compose_strip(
        storyboard=storyboard,
        panel_image_paths=panel_paths,
        output_png=paths.composite_dir / model_key / "strip.png",
        output_pdf=paths.composite_dir / model_key / "strip.pdf",
    )
    store.append_registry(
        {
            "run_id": run_id,
            "event": "reroll_panel",
            "model": model_key,
            "panel": panel_number,
            "metaphor": metaphor,
        }
    )
    return str(output_path)
