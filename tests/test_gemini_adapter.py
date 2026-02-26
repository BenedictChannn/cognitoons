from pathlib import Path

from comicstrip_tutor.image_models.base import PanelImageRequest
from comicstrip_tutor.image_models.gemini_image import GeminiImageModel
from comicstrip_tutor.image_models.reliability import CircuitBreakerStore, ReliabilityPolicy


class _InlineData:
    def __init__(self, data: bytes):
        self.data = data


class _Part:
    def __init__(self, data: bytes):
        self.inline_data = _InlineData(data)


class _Content:
    def __init__(self, data: bytes):
        self.parts = [_Part(data)]


class _Candidate:
    def __init__(self, data: bytes):
        self.content = _Content(data)


class _Response:
    def __init__(self, data: bytes):
        self.candidates = [_Candidate(data)]
        self.usage_metadata = {"total_tokens": 42}


class _Models:
    def __init__(self, data: bytes):
        self._data = data

    def generate_content(self, **_: object) -> _Response:
        return _Response(self._data)


class _Client:
    def __init__(self, data: bytes):
        self.models = _Models(data)


def test_gemini_adapter_generate_content_path(tmp_path: Path) -> None:
    model = GeminiImageModel(
        "gemini-2.5-flash-image",
        "cheap",
        api_key=None,
        reliability_policy=ReliabilityPolicy(
            timeout_s=10,
            max_retries=0,
            backoff_s=0,
            circuit_fail_threshold=2,
            circuit_cooldown_s=10,
        ),
        circuit_store=CircuitBreakerStore(tmp_path / "provider_circuit.json"),
    )
    model._client = _Client(b"fake-image-bytes")
    out_path = tmp_path / "panel.png"
    result = model.generate_panel_image(
        PanelImageRequest(
            panel_number=1,
            prompt="Test prompt",
            width=256,
            height=256,
            style_guide="style",
            output_path=str(out_path),
            dry_run=False,
        )
    )
    assert out_path.exists()
    assert result.provider_usage["total_tokens"] == 42
