from pathlib import Path

import pytest

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline import render_pipeline
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import read_json


class _TimeoutModel:
    provider = "test"

    def generate_panel_image(self, request):
        raise TimeoutError(f"timed out for panel {request.panel_number}")


def test_render_writes_failure_manifest_on_provider_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_config = AppConfig(
        openai_api_key=None,
        gemini_api_key=None,
        output_root=tmp_path / "runs",
        provider_timeout_s=5,
        provider_max_retries=0,
        provider_backoff_s=0,
        circuit_fail_threshold=1,
        circuit_cooldown_s=10,
        enable_experimental_models=False,
        gemini_text_image_fallback=False,
    )
    store = ArtifactStore(app_config.output_root)
    run_planning_pipeline(
        run_config=RunConfig(
            run_id="failure-manifest",
            topic="Explain lock-free queues",
            panel_count=4,
            mode="draft",
            critique_mode="warn",
        ),
        artifact_store=store,
    )
    monkeypatch.setattr(render_pipeline, "create_model", lambda *_args, **_kwargs: _TimeoutModel())

    with pytest.raises(RuntimeError):
        render_pipeline.render_storyboard(
            run_id="failure-manifest",
            model_key="gpt-image-1-mini",
            mode="draft",
            dry_run=False,
            app_config=app_config,
        )

    manifest_path = app_config.output_root / "failure-manifest" / "manifest_gpt-image-1-mini.json"
    manifest = read_json(manifest_path)
    assert manifest["completion_status"] == "failure"
    assert manifest["error_type"] == "provider_timeout"
