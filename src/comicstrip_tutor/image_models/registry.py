"""Model registry and factory."""

from __future__ import annotations

from typing import Literal, TypedDict

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.base import ImageModel, ModelTier
from comicstrip_tutor.image_models.gemini_image import GeminiImageModel
from comicstrip_tutor.image_models.openai_image import OpenAIImageModel


class ModelMeta(TypedDict):
    provider: Literal["openai", "google"]
    tier: ModelTier


MODEL_METADATA: dict[str, ModelMeta] = {
    "gpt-image-1-mini": {"provider": "openai", "tier": "cheap"},
    "gpt-image-1": {"provider": "openai", "tier": "mid"},
    "gpt-image-1.5": {"provider": "openai", "tier": "premium"},
    "gemini-2.5-flash-image": {"provider": "google", "tier": "cheap"},
    "gemini-3-pro-image-preview": {"provider": "google", "tier": "premium"},
}


def list_models() -> list[str]:
    """List supported image model keys."""
    return list(MODEL_METADATA.keys())


def create_model(model_key: str, config: AppConfig) -> ImageModel:
    """Create model adapter for model key."""
    if model_key not in MODEL_METADATA:
        supported = ", ".join(list_models())
        raise ValueError(f"Unsupported model '{model_key}'. Supported: {supported}")
    metadata = MODEL_METADATA[model_key]
    provider = metadata["provider"]
    tier: ModelTier = metadata["tier"]
    if provider == "openai":
        return OpenAIImageModel(model_id=model_key, tier=tier, api_key=config.openai_api_key)
    return GeminiImageModel(model_id=model_key, tier=tier, api_key=config.gemini_api_key)
