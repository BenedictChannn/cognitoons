"""Comparison pipeline for same storyboard across models."""

from __future__ import annotations

from comicstrip_tutor.composition.compare_composer import compose_comparison
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline.render_pipeline import render_storyboard
from comicstrip_tutor.schemas.runs import CompareRunSummary
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import read_json, write_json


def compare_models_on_storyboard(
    *,
    run_id: str,
    model_a: str,
    model_b: str,
    mode: str,
    dry_run: bool,
    app_config: AppConfig,
) -> CompareRunSummary:
    """Render two models and create side-by-side panel comparison."""
    render_storyboard(
        run_id=run_id,
        model_key=model_a,
        mode=mode,
        dry_run=dry_run,
        app_config=app_config,
    )
    render_storyboard(
        run_id=run_id,
        model_key=model_b,
        mode=mode,
        dry_run=dry_run,
        app_config=app_config,
    )
    store = ArtifactStore(app_config.output_root)
    paths = store.open_run(run_id)

    panel_count = len(read_json(paths.root / "storyboard.json")["panels"])
    panel_paths_a = [
        str(paths.images_dir / model_a / f"panel_{idx:02d}.png")
        for idx in range(1, panel_count + 1)
    ]
    panel_paths_b = [
        str(paths.images_dir / model_b / f"panel_{idx:02d}.png")
        for idx in range(1, panel_count + 1)
    ]
    output_path = paths.composite_dir / f"compare_{model_a}_vs_{model_b}.png"
    compose_comparison(
        panel_paths_a=panel_paths_a,
        panel_paths_b=panel_paths_b,
        model_a=model_a,
        model_b=model_b,
        output_path=output_path,
    )
    summary = CompareRunSummary(
        run_id=run_id,
        model_a=model_a,
        model_b=model_b,
        output_path=str(output_path),
    )
    write_json(paths.root / f"compare_{model_a}_vs_{model_b}.json", summary.model_dump())
    store.append_registry(
        {"run_id": run_id, "event": "compare_complete", "model_a": model_a, "model_b": model_b}
    )
    return summary
