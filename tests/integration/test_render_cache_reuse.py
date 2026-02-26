from pathlib import Path

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.pipeline.render_pipeline import render_storyboard
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore


def test_render_cache_reuses_previous_panel_outputs(tmp_path: Path) -> None:
    output_root = tmp_path / "runs" / "experiments"
    app_config = AppConfig(
        openai_api_key=None,
        gemini_api_key=None,
        output_root=output_root,
        provider_timeout_s=30,
        provider_max_retries=1,
        provider_backoff_s=0.2,
        circuit_fail_threshold=2,
        circuit_cooldown_s=30,
        enable_experimental_models=False,
        gemini_text_image_fallback=False,
    )
    store = ArtifactStore(output_root=output_root)
    run_config = RunConfig(
        run_id="cache-reuse",
        topic="Explain UCT in MCTS to a beginner",
        panel_count=4,
        mode="draft",
    )
    run_planning_pipeline(run_config=run_config, artifact_store=store)
    first_manifest = render_storyboard(
        run_id="cache-reuse",
        model_key="gpt-image-1-mini",
        mode="draft",
        dry_run=True,
        app_config=app_config,
    )
    second_manifest = render_storyboard(
        run_id="cache-reuse",
        model_key="gpt-image-1-mini",
        mode="draft",
        dry_run=True,
        app_config=app_config,
    )
    assert first_manifest.total_estimated_cost_usd > 0
    assert second_manifest.total_estimated_cost_usd == 0
