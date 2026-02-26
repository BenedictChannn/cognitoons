from pathlib import Path

from PIL import Image

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.pipeline import render_pipeline
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore


class _FailingModel:
    provider = "google"

    def generate_panel_image(self, request):
        raise RuntimeError("simulated provider hang")


class _FallbackModel:
    provider = "google"

    def generate_panel_image(self, request):
        out = Path(request.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (request.width, request.height), color=(250, 250, 250)).save(out)
        return render_pipeline.PanelImageResult(
            image_path=str(out),
            provider_usage={"mode": "fallback"},
            estimated_cost_usd=0.012,
        )


def test_render_uses_fallback_for_gemini_3(tmp_path: Path, monkeypatch) -> None:
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
            run_id="fallback-test",
            topic="Explain eventual consistency",
            panel_count=4,
            mode="draft",
            critique_mode="warn",
        ),
        artifact_store=store,
    )

    def _fake_create_model(model_key: str, _config: AppConfig):
        if model_key == "gemini-3-pro-image-preview":
            return _FailingModel()
        return _FallbackModel()

    monkeypatch.setattr(render_pipeline, "create_model", _fake_create_model)
    manifest = render_pipeline.render_storyboard(
        run_id="fallback-test",
        model_key="gemini-3-pro-image-preview",
        mode="draft",
        dry_run=False,
        app_config=app_config,
        allow_model_fallback=True,
    )
    assert any("Fallback used" in note for note in manifest.notes)
