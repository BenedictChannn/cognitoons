from pathlib import Path

from google.genai import types as genai_types

from comicstrip_tutor.image_models.base import PanelImageRequest
from comicstrip_tutor.image_models.gemini_image import GeminiImageModel
from comicstrip_tutor.image_models.reliability import CircuitBreakerStore, ReliabilityPolicy


class _InlineData:
    def __init__(self, data: bytes):
        self.data = data


class _Part:
    def __init__(self, data: bytes | None = None, text: str | None = None):
        self.inline_data = _InlineData(data) if data is not None else None
        self.text = text


class _Content:
    def __init__(self, parts: list[_Part]):
        self.parts = parts


class _Candidate:
    def __init__(self, parts: list[_Part], finish_reason: str | None = None):
        self.content = _Content(parts)
        self.finish_reason = finish_reason


class _Response:
    def __init__(self, parts: list[_Part]):
        self.candidates = [_Candidate(parts, finish_reason="STOP")]
        self.usage_metadata = {"total_tokens": 42}


class _Models:
    def __init__(self, response: _Response):
        self._response = response
        self.last_config = None

    def generate_content(self, **kwargs: object) -> _Response:
        self.last_config = kwargs.get("config")
        return self._response


class _Client:
    def __init__(self, response: _Response):
        self.models = _Models(response)


class _SequenceModels:
    def __init__(self, responses: list[_Response]):
        self._responses = responses
        self.requested_modalities: list[list[str]] = []

    def generate_content(self, **kwargs: object) -> _Response:
        config = kwargs.get("config")
        assert isinstance(config, genai_types.GenerateContentConfig)
        modalities = [str(item) for item in (config.response_modalities or [])]
        self.requested_modalities.append(modalities)
        return self._responses.pop(0)


class _SequenceClient:
    def __init__(self, responses: list[_Response]):
        self.models = _SequenceModels(responses)


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
        allow_text_image_fallback=False,
    )
    model._client = _Client(
        _Response(parts=[_Part(data=b"fake-image-bytes"), _Part(text="diagnostic text")])
    )
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
    config = model._client.models.last_config
    assert isinstance(config, genai_types.GenerateContentConfig)
    assert config.response_modalities == [genai_types.Modality.IMAGE]
    assert config.response_mime_type is None
    assert config.response_schema is None
    diagnostics = result.provider_usage["response_diagnostics"]
    assert diagnostics["candidate_count"] == 1
    assert diagnostics["inline_data_part_count"] == 1
    assert diagnostics["text_part_count"] == 1


def test_gemini_adapter_uses_controlled_text_image_fallback(tmp_path: Path) -> None:
    model = GeminiImageModel(
        "gemini-3-pro-image-preview",
        "premium",
        api_key=None,
        reliability_policy=ReliabilityPolicy(
            timeout_s=10,
            max_retries=0,
            backoff_s=0,
            circuit_fail_threshold=2,
            circuit_cooldown_s=10,
        ),
        circuit_store=CircuitBreakerStore(tmp_path / "provider_circuit.json"),
        allow_text_image_fallback=True,
    )
    model._client = _SequenceClient(
        responses=[
            _Response(parts=[_Part(text="No image in first attempt")]),
            _Response(parts=[_Part(data=b"fallback-image-bytes")]),
        ]
    )
    out_path = tmp_path / "panel_fallback.png"
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
    assert result.provider_usage["strategy_fallback_used"] is True
    assert model._client.models.requested_modalities == [
        ["IMAGE"],
        ["TEXT", "IMAGE"],
    ]
