"""Gemini image adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from google import genai

from comicstrip_tutor.image_models.base import (
    ImageModel,
    ModelTier,
    PanelImageRequest,
    PanelImageResult,
)
from comicstrip_tutor.image_models.mock_render import create_placeholder_image
from comicstrip_tutor.image_models.pricing import estimate_cost


class GeminiImageModel(ImageModel):
    """Gemini image model wrapper."""

    def __init__(self, model_id: str, tier: ModelTier, api_key: str | None):
        self.model_id = model_id
        self.provider = "google"
        self.tier = tier
        self.supports_reference_images = False
        self._client = genai.Client(api_key=api_key) if api_key else None

    def generate_panel_image(self, request: PanelImageRequest) -> PanelImageResult:
        final_prompt = f"{request.style_guide}\n\nPanel {request.panel_number}\n{request.prompt}"
        if request.dry_run or self._client is None:
            create_placeholder_image(
                output_path=request.output_path,
                title=f"{self.model_id} (dry-run)",
                prompt=final_prompt,
                width=request.width,
                height=request.height,
            )
            return PanelImageResult(
                image_path=request.output_path,
                provider_usage={"mode": "dry_run"},
                estimated_cost_usd=estimate_cost(self.model_id, 1),
            )

        response = self._client.models.generate_images(
            model=self.model_id,
            prompt=final_prompt,
            config={"number_of_images": 1},
        )
        generated_images = getattr(response, "generated_images", None) or []
        if not generated_images:
            raise RuntimeError(f"No generated images returned for {self.model_id}")
        generated_image = generated_images[0].image
        image_bytes = getattr(generated_image, "image_bytes", None)
        if image_bytes is None:
            raise RuntimeError(f"No image bytes returned for {self.model_id}")
        out_path = Path(request.output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image_bytes)
        usage: dict[str, Any] = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = cast(dict[str, Any], response.usage_metadata)
        return PanelImageResult(
            image_path=request.output_path,
            provider_usage=usage,
            estimated_cost_usd=estimate_cost(self.model_id, 1),
        )
