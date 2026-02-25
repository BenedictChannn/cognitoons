from pathlib import Path

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline.compare_pipeline import compare_models_on_storyboard
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore


def test_mock_compare_flow(tmp_path: Path) -> None:
    config = AppConfig(openai_api_key=None, gemini_api_key=None, output_root=tmp_path)
    store = ArtifactStore(tmp_path)
    run_planning_pipeline(
        run_config=RunConfig(
            run_id="it-compare",
            topic="Explain caching tradeoffs",
            panel_count=4,
            mode="draft",
        ),
        artifact_store=store,
    )
    summary = compare_models_on_storyboard(
        run_id="it-compare",
        model_a="gpt-image-1-mini",
        model_b="gemini-2.5-flash-image",
        mode="draft",
        dry_run=True,
        app_config=config,
    )
    assert Path(summary.output_path).exists()
