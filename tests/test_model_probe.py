from pathlib import Path

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.base import PanelImageResult
from comicstrip_tutor.probes import model_probe


class _ProbeModel:
    provider = "google"

    def __init__(self) -> None:
        self.calls = 0

    def generate_panel_image(self, request):
        self.calls += 1
        output_path = Path(request.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"png")
        return PanelImageResult(
            image_path=str(output_path),
            provider_usage={"response_diagnostics": {"inline_data_part_count": 1}},
            estimated_cost_usd=0.01,
        )


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        openai_api_key=None,
        gemini_api_key=None,
        output_root=tmp_path / "runs",
        provider_timeout_s=10,
        provider_max_retries=0,
        provider_backoff_s=0.0,
        circuit_fail_threshold=1,
        circuit_cooldown_s=10,
        enable_experimental_models=False,
        gemini_text_image_fallback=False,
    )


def test_run_model_probe_persists_probe_artifact(tmp_path: Path, monkeypatch) -> None:
    probe_model_instance = _ProbeModel()
    monkeypatch.setattr(model_probe, "create_model", lambda *_args, **_kwargs: probe_model_instance)

    result = model_probe.run_model_probe(
        model_key="gemini-3-pro-image-preview",
        prompt="Probe prompt",
        repetitions=3,
        width=256,
        height=256,
        dry_run=False,
        app_config=_config(tmp_path),
    )

    assert result.success_count == 3
    assert result.failure_count == 0
    assert result.success_rate == 1.0
    probe_json = _config(tmp_path).output_root / result.probe_id / "probe_result.json"
    assert probe_json.exists()


def test_run_model_probe_records_init_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        model_probe,
        "create_model",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("experimental disabled")),
    )

    result = model_probe.run_model_probe(
        model_key="gemini-3.1-flash-image-preview",
        prompt="Probe prompt",
        repetitions=2,
        width=256,
        height=256,
        dry_run=False,
        app_config=_config(tmp_path),
    )

    assert result.success_count == 0
    assert result.failure_count == 1
    assert result.attempts[0].error_type == "experimental_model_disabled"
