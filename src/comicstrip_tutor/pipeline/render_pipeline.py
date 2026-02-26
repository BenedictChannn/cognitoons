"""Rendering pipeline: per-panel generation + composition + scoring."""

from __future__ import annotations

from pathlib import Path
from shutil import copy2

from pydantic import TypeAdapter

from comicstrip_tutor.composition.strip_composer import compose_strip
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.critique.orchestrator import should_block_render
from comicstrip_tutor.evaluation.scorer import score_render_run
from comicstrip_tutor.image_models.base import ImageModel, PanelImageRequest, PanelImageResult
from comicstrip_tutor.image_models.registry import create_model
from comicstrip_tutor.pipeline.critique_pipeline import run_critique_with_rewrites
from comicstrip_tutor.pipeline.error_taxonomy import classify_render_exception
from comicstrip_tutor.pipeline.panel_prompt_builder import build_panel_prompt
from comicstrip_tutor.schemas.runs import (
    CritiqueMode,
    ImageTextMode,
    PanelRenderRecord,
    RenderCompletionStatus,
    RenderRunManifest,
    RunConfig,
)
from comicstrip_tutor.schemas.storyboard import Storyboard
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.cache import JsonCache
from comicstrip_tutor.storage.io_utils import read_json, write_json, write_text
from comicstrip_tutor.utils.hashing import sha256_text

_STORYBOARD_ADAPTER = TypeAdapter(Storyboard)
_RUN_CONFIG_ADAPTER = TypeAdapter(RunConfig)


def _size_for_mode(mode: str) -> tuple[int, int]:
    if mode == "publish":
        return (1024, 1024)
    return (768, 768)


def _panel_cache_key(
    *,
    model_key: str,
    mode: str,
    width: int,
    height: int,
    style_guide: str,
    prompt: str,
) -> str:
    return sha256_text(
        "|".join([model_key, mode, f"{width}x{height}", style_guide.strip(), prompt.strip()])
    )


def render_storyboard(
    *,
    run_id: str,
    model_key: str,
    mode: str,
    dry_run: bool,
    app_config: AppConfig,
    expected_key_points: list[str] | None = None,
    misconceptions: list[str] | None = None,
    enable_llm_judge: bool = False,
    critique_mode: CritiqueMode | None = None,
    image_text_mode: ImageTextMode | None = None,
    allow_model_fallback: bool = True,
    auto_rewrite: bool | None = None,
    critique_max_iterations: int | None = None,
) -> RenderRunManifest:
    """Render storyboard with selected image model."""
    store = ArtifactStore(app_config.output_root)
    paths = store.open_run(run_id)
    storyboard = _STORYBOARD_ADAPTER.validate_python(read_json(paths.root / "storyboard.json"))
    run_config = _RUN_CONFIG_ADAPTER.validate_python(read_json(paths.root / "run_config.json"))
    model = create_model(model_key, app_config)
    fallback_model: ImageModel | None = None
    width, height = _size_for_mode(mode)
    panel_cache = JsonCache(app_config.output_root.parent / "panel_cache.json")
    resolved_critique_mode = critique_mode or run_config.critique_mode
    resolved_image_text_mode = image_text_mode or run_config.image_text_mode
    resolved_auto_rewrite = run_config.auto_rewrite if auto_rewrite is None else auto_rewrite
    resolved_critique_max_iterations = (
        run_config.critique_max_iterations
        if critique_max_iterations is None
        else critique_max_iterations
    )
    if resolved_critique_max_iterations is None:
        resolved_critique_max_iterations = 4 if mode == "publish" else 2
    resolved_expected_key_points = list(expected_key_points or [])
    resolved_misconceptions = list(misconceptions or [])

    learning_plan_path = paths.planning_dir / "learning_plan.json"
    if learning_plan_path.exists():
        learning_plan_payload = read_json(learning_plan_path)
        if not resolved_expected_key_points:
            resolved_expected_key_points = [
                str(entry) for entry in learning_plan_payload.get("objectives", [])
            ]
        if not resolved_misconceptions:
            resolved_misconceptions = [
                str(entry) for entry in learning_plan_payload.get("misconceptions", [])
            ]

    storyboard, critique_report, rewrite_count = run_critique_with_rewrites(
        run_id=run_id,
        stage=f"pre_render_{model_key}",
        critique_mode=resolved_critique_mode,
        storyboard=storyboard,
        expected_key_points=resolved_expected_key_points,
        misconceptions=resolved_misconceptions,
        audience_level=storyboard.audience_level,
        output_dir=paths.critiques_dir,
        max_iterations=resolved_critique_max_iterations,
        auto_rewrite=resolved_auto_rewrite,
    )
    if rewrite_count > 0:
        write_json(paths.root / "storyboard.json", storyboard.model_dump())
    if should_block_render(critique_report):
        raise RuntimeError(
            "Render blocked by critique gate after rewrite loop: "
            f"{critique_report.blocking_issue_count} critical and "
            f"{critique_report.major_issue_count} major issues."
        )

    model_image_dir = paths.images_dir / model_key
    model_image_dir.mkdir(parents=True, exist_ok=True)
    prompt_files: list[Path] = []
    image_files: list[Path] = []
    panel_records: list[PanelRenderRecord] = []
    prompts_joined: list[str] = []
    manifest_notes: list[str] = []
    if rewrite_count > 0:
        manifest_notes.append(f"Auto rewrite iterations applied before render: {rewrite_count}")

    def _generate_panel_image(
        output_path: Path, panel_number: int, prompt: str
    ) -> PanelImageResult:
        nonlocal fallback_model
        request = PanelImageRequest(
            panel_number=panel_number,
            prompt=prompt,
            width=width,
            height=height,
            style_guide=storyboard.character_style_guide,
            output_path=str(output_path),
            dry_run=dry_run,
        )
        try:
            return model.generate_panel_image(request)
        except Exception as exc:  # noqa: BLE001
            if not (allow_model_fallback and model_key == "gemini-3-pro-image-preview"):
                raise
            if fallback_model is None:
                fallback_model = create_model("gemini-2.5-flash-image", app_config)
            fallback_result = fallback_model.generate_panel_image(request)
            fallback_usage = {
                **fallback_result.provider_usage,
                "fallback_from_model": model_key,
                "fallback_to_model": "gemini-2.5-flash-image",
                "fallback_reason": str(exc),
            }
            manifest_notes.append(
                "Fallback used: gemini-3-pro-image-preview -> gemini-2.5-flash-image"
            )
            return PanelImageResult(
                image_path=fallback_result.image_path,
                provider_usage=fallback_usage,
                estimated_cost_usd=fallback_result.estimated_cost_usd,
            )

    completion_status: RenderCompletionStatus = "success"
    error_type: str | None = None
    error_message: str | None = None
    caught_exception: Exception | None = None
    evaluation = None

    try:
        for panel in storyboard.panels:
            prompt = build_panel_prompt(
                storyboard,
                panel,
                image_text_mode=resolved_image_text_mode,
            )
            prompt_file = paths.prompts_dir / f"panel_{panel.panel_number:02d}.txt"
            write_text(prompt_file, prompt + "\n")
            prompt_files.append(prompt_file)
            prompts_joined.append(prompt)

            output_path = model_image_dir / f"panel_{panel.panel_number:02d}.png"
            cache_key = _panel_cache_key(
                model_key=model_key,
                mode=mode,
                width=width,
                height=height,
                style_guide=storyboard.character_style_guide,
                prompt=prompt,
            )
            cache_hit = panel_cache.get(cache_key)
            result: PanelImageResult
            if cache_hit and isinstance(cache_hit.get("image_path"), str):
                cached_image_path = Path(cache_hit["image_path"])
                if cached_image_path.exists():
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    if cached_image_path != output_path:
                        copy2(cached_image_path, output_path)
                    result = PanelImageResult(
                        image_path=str(output_path),
                        provider_usage={
                            "cache_hit": True,
                            "source_image_path": str(cached_image_path),
                        },
                        estimated_cost_usd=0.0,
                    )
                else:
                    result = _generate_panel_image(output_path, panel.panel_number, prompt)
            else:
                result = _generate_panel_image(output_path, panel.panel_number, prompt)
            panel_cache.set(
                cache_key,
                {
                    "image_path": str(output_path),
                    "model_key": model_key,
                    "mode": mode,
                    "prompt_hash": sha256_text(prompt),
                },
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
        evaluation = score_render_run(
            run_id=run_id,
            model_key=model_key,
            storyboard=storyboard,
            expected_key_points=resolved_expected_key_points,
            prompt_paths=prompt_files,
            image_paths=image_files,
            enable_llm_judge=enable_llm_judge,
            critique_report=critique_report,
        )
        if mode == "publish" and resolved_critique_mode == "strict" and not evaluation.publishable:
            raise ValueError("publish_gate_blocked: " + "; ".join(evaluation.publishable_reasons))
    except Exception as exc:  # noqa: BLE001
        caught_exception = exc
        error_type, error_message = classify_render_exception(exc)
        completion_status = "partial_success" if panel_records else "failure"
        manifest_notes.append(f"render_error={error_type}")

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
        completion_status=completion_status,
        error_type=error_type,
        error_message=error_message,
        notes=list(dict.fromkeys(manifest_notes)),
    )
    write_json(paths.root / f"manifest_{model_key}.json", manifest.model_dump())

    if evaluation is not None:
        write_json(paths.evaluations_dir / f"{model_key}.json", evaluation.model_dump())
        store.append_registry(
            {
                "run_id": run_id,
                "event": "render_complete",
                "model": model_key,
                "aggregate_score": evaluation.metrics.aggregate,
                "estimated_cost_usd": manifest.total_estimated_cost_usd,
                "critique_score": critique_report.overall_score,
                "critique_mode": resolved_critique_mode,
                "completion_status": completion_status,
            }
        )
    else:
        store.append_registry(
            {
                "run_id": run_id,
                "event": "render_failed",
                "model": model_key,
                "error_type": error_type or "unknown_failure",
                "error_message": error_message or "",
                "estimated_cost_usd": manifest.total_estimated_cost_usd,
                "completion_status": completion_status,
            }
        )

    if caught_exception is not None:
        raise RuntimeError(
            f"Render ended with {completion_status}: {error_type} - {error_message}"
        ) from caught_exception
    return manifest
