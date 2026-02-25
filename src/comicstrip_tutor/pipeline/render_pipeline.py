"""Rendering pipeline: per-panel generation + composition + scoring."""

from __future__ import annotations

from pathlib import Path

from pydantic import TypeAdapter

from comicstrip_tutor.composition.strip_composer import compose_strip
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.evaluation.scorer import score_render_run
from comicstrip_tutor.image_models.base import PanelImageRequest
from comicstrip_tutor.image_models.registry import create_model
from comicstrip_tutor.pipeline.panel_prompt_builder import build_panel_prompt
from comicstrip_tutor.schemas.runs import PanelRenderRecord, RenderRunManifest
from comicstrip_tutor.schemas.storyboard import Storyboard
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import read_json, write_json, write_text
from comicstrip_tutor.utils.hashing import sha256_text

_STORYBOARD_ADAPTER = TypeAdapter(Storyboard)


def _size_for_mode(mode: str) -> tuple[int, int]:
    if mode == "publish":
        return (1024, 1024)
    return (768, 768)


def render_storyboard(
    *,
    run_id: str,
    model_key: str,
    mode: str,
    dry_run: bool,
    app_config: AppConfig,
    expected_key_points: list[str] | None = None,
    enable_llm_judge: bool = False,
) -> RenderRunManifest:
    """Render storyboard with selected image model."""
    store = ArtifactStore(app_config.output_root)
    paths = store.open_run(run_id)
    storyboard = _STORYBOARD_ADAPTER.validate_python(read_json(paths.root / "storyboard.json"))
    model = create_model(model_key, app_config)
    width, height = _size_for_mode(mode)

    model_image_dir = paths.images_dir / model_key
    model_image_dir.mkdir(parents=True, exist_ok=True)
    prompt_files: list[Path] = []
    image_files: list[Path] = []
    panel_records: list[PanelRenderRecord] = []
    prompts_joined: list[str] = []

    for panel in storyboard.panels:
        prompt = build_panel_prompt(storyboard, panel)
        prompt_file = paths.prompts_dir / f"panel_{panel.panel_number:02d}.txt"
        write_text(prompt_file, prompt + "\n")
        prompt_files.append(prompt_file)
        prompts_joined.append(prompt)

        output_path = model_image_dir / f"panel_{panel.panel_number:02d}.png"
        result = model.generate_panel_image(
            PanelImageRequest(
                panel_number=panel.panel_number,
                prompt=prompt,
                width=width,
                height=height,
                style_guide=storyboard.character_style_guide,
                output_path=str(output_path),
                dry_run=dry_run,
            )
        )
        image_files.append(Path(result.image_path))
        panel_records.append(
            PanelRenderRecord(
                panel_number=panel.panel_number,
                prompt_path=str(prompt_file),
                image_path=result.image_path,
                estimated_cost_usd=result.estimated_cost_usd,
                provider_usage=result.provider_usage,
            )
        )

    output_strip_png = paths.composite_dir / model_key / "strip.png"
    output_strip_pdf = paths.composite_dir / model_key / "strip.pdf"
    compose_strip(
        storyboard=storyboard,
        panel_image_paths=[str(path) for path in image_files],
        output_png=output_strip_png,
        output_pdf=output_strip_pdf,
    )
    prompt_hash = sha256_text("\n".join(prompts_joined))
    storyboard_hash = sha256_text(storyboard.model_dump_json())
    manifest = RenderRunManifest(
        run_id=run_id,
        model_key=model_key,
        provider=model.provider,
        mode=mode,  # type: ignore[arg-type]
        storyboard_hash=storyboard_hash,
        prompt_hash=prompt_hash,
        panel_records=panel_records,
        total_estimated_cost_usd=round(
            sum(record.estimated_cost_usd for record in panel_records), 4
        ),
    )
    write_json(paths.root / f"manifest_{model_key}.json", manifest.model_dump())

    evaluation = score_render_run(
        run_id=run_id,
        model_key=model_key,
        storyboard=storyboard,
        expected_key_points=expected_key_points or [],
        prompt_paths=prompt_files,
        image_paths=image_files,
        enable_llm_judge=enable_llm_judge,
    )
    write_json(paths.evaluations_dir / f"{model_key}.json", evaluation.model_dump())
    store.append_registry(
        {
            "run_id": run_id,
            "event": "render_complete",
            "model": model_key,
            "aggregate_score": evaluation.metrics.aggregate,
            "estimated_cost_usd": manifest.total_estimated_cost_usd,
        }
    )
    return manifest
