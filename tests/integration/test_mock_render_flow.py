from pathlib import Path

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.pipeline.render_pipeline import render_storyboard
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore


def test_mock_render_flow(tmp_path: Path) -> None:
    app_config = AppConfig(openai_api_key=None, gemini_api_key=None, output_root=tmp_path)
    store = ArtifactStore(tmp_path)
    run_config = RunConfig(
        run_id="it-render",
        topic="Explain UCT in MCTS to a beginner",
        panel_count=6,
        mode="draft",
    )
    run_planning_pipeline(run_config=run_config, artifact_store=store)
    manifest = render_storyboard(
        run_id="it-render",
        model_key="gpt-image-1-mini",
        mode="draft",
        dry_run=True,
        app_config=app_config,
    )
    assert manifest.total_estimated_cost_usd > 0
    assert (tmp_path / "it-render" / "composite" / "gpt-image-1-mini" / "strip.png").exists()
