"""Model registry and factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.base import ImageModel, ModelTier
from comicstrip_tutor.image_models.gemini_image import GeminiImageModel
from comicstrip_tutor.image_models.openai_image import OpenAIImageModel
from comicstrip_tutor.image_models.reliability import CircuitBreakerStore, ReliabilityPolicy


class ModelMeta(TypedDict):
    provider: Literal["openai", "google"]
    tier: ModelTier
    experimental: bool
    fallback_model: str | None


MODEL_METADATA: dict[str, ModelMeta] = {
    "gpt-image-1-mini": {
        "provider": "openai",
        "tier": "cheap",
        "experimental": False,
        "fallback_model": None,
    },
    "gpt-image-1": {
        "provider": "openai",
        "tier": "mid",
        "experimental": False,
        "fallback_model": None,
    },
    "gpt-image-1.5": {
        "provider": "openai",
        "tier": "premium",
        "experimental": False,
        "fallback_model": None,
    },
    "gemini-2.5-flash-image": {
        "provider": "google",
        "tier": "cheap",
        "experimental": False,
        "fallback_model": None,
    },
    "gemini-3-pro-image-preview": {
        "provider": "google",
        "tier": "premium",
        "experimental": False,
        "fallback_model": "gemini-2.5-flash-image",
    },
    "gemini-3.1-flash-image-preview": {
        "provider": "google",
        "tier": "mid",
        "experimental": True,
        "fallback_model": "gemini-2.5-flash-image",
    },
}


def list_models() -> list[str]:
    """List supported image model keys."""
    return list(MODEL_METADATA.keys())


@dataclass(slots=True, frozen=True)
class ModelDescriptor:
    """Expanded metadata descriptor for CLI/reporting surfaces."""

    key: str
    provider: Literal["openai", "google"]
    tier: ModelTier
    experimental: bool
    fallback_model: str | None


def list_model_descriptors() -> list[ModelDescriptor]:
    """Return model descriptors with capability flags."""
    return [
        ModelDescriptor(
            key=model_key,
            provider=metadata["provider"],
            tier=metadata["tier"],
            experimental=metadata["experimental"],
            fallback_model=metadata["fallback_model"],
        )
        for model_key, metadata in MODEL_METADATA.items()
    ]


def fallback_model_for(model_key: str) -> str | None:
    """Resolve explicit fallback model configured for a model key."""
    metadata = MODEL_METADATA.get(model_key)
    if metadata is None:
        return None
    return metadata["fallback_model"]


def provider_for(model_key: str) -> str:
    """Resolve provider string for a model key."""
    metadata = MODEL_METADATA.get(model_key)
    if metadata is None:
        return "unknown"
    return metadata["provider"]


def create_model(model_key: str, config: AppConfig) -> ImageModel:
    """Create model adapter for model key."""
    if model_key not in MODEL_METADATA:
        supported = ", ".join(list_models())
        raise ValueError(f"Unsupported model '{model_key}'. Supported: {supported}")
    metadata = MODEL_METADATA[model_key]
    provider = metadata["provider"]
    tier: ModelTier = metadata["tier"]
    if metadata["experimental"] and not config.enable_experimental_models:
        raise ValueError(
            f"Model '{model_key}' is experimental. "
            "Enable COMIC_TUTOR_ENABLE_EXPERIMENTAL_MODELS=true to use it."
        )
    reliability_policy = ReliabilityPolicy(
        timeout_s=config.provider_timeout_s,
        max_retries=config.provider_max_retries,
        backoff_s=config.provider_backoff_s,
        circuit_fail_threshold=config.circuit_fail_threshold,
        circuit_cooldown_s=config.circuit_cooldown_s,
    )
    circuit_store = CircuitBreakerStore(config.output_root.parent / "provider_circuit.json")
    if provider == "openai":
        return OpenAIImageModel(
            model_id=model_key,
            tier=tier,
            api_key=config.openai_api_key,
            reliability_policy=reliability_policy,
            circuit_store=circuit_store,
        )
    return GeminiImageModel(
        model_id=model_key,
        tier=tier,
        api_key=config.gemini_api_key,
        reliability_policy=reliability_policy,
        circuit_store=circuit_store,
        allow_text_image_fallback=config.gemini_text_image_fallback,
    )
