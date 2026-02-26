from pathlib import Path

import pytest

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.registry import create_model, list_model_descriptors


def _base_config(enable_experimental_models: bool) -> AppConfig:
    return AppConfig(
        openai_api_key=None,
        gemini_api_key=None,
        output_root=Path("runs/experiments"),
        provider_timeout_s=30,
        provider_max_retries=1,
        provider_backoff_s=0.1,
        circuit_fail_threshold=2,
        circuit_cooldown_s=30,
        enable_experimental_models=enable_experimental_models,
        gemini_text_image_fallback=False,
    )


def test_list_model_descriptors_marks_nano_banana_2_experimental() -> None:
    descriptors = {entry.key: entry for entry in list_model_descriptors()}
    assert "gemini-3.1-flash-image-preview" in descriptors
    assert descriptors["gemini-3.1-flash-image-preview"].experimental is True
    assert descriptors["gemini-3.1-flash-image-preview"].fallback_model == "gemini-2.5-flash-image"


def test_create_model_blocks_experimental_when_disabled() -> None:
    with pytest.raises(ValueError, match="experimental"):
        create_model("gemini-3.1-flash-image-preview", _base_config(False))


def test_create_model_allows_experimental_when_enabled() -> None:
    model = create_model("gemini-3.1-flash-image-preview", _base_config(True))
    assert model.provider == "google"
