"""OpenAI GPT Image adapter."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Literal, cast

from openai import OpenAI

from comicstrip_tutor.image_models.base import (
    ImageModel,
    ModelTier,
    PanelImageRequest,
    PanelImageResult,
)
from comicstrip_tutor.image_models.mock_render import create_placeholder_image
from comicstrip_tutor.image_models.pricing import estimate_cost

OpenAIImageSize = Literal[
    "auto",
    "1024x1024",
    "1536x1024",
    "1024x1536",
    "256x256",
    "512x512",
    "1792x1024",
    "1024x1792",
]


def _size_str(width: int, height: int) -> OpenAIImageSize:
    if width == height:
        return "1024x1024"
    if width > height:
        return "1536x1024"
    return "1024x1536"


class OpenAIImageModel(ImageModel):
    """OpenAI image model wrapper."""

    def __init__(self, model_id: str, tier: ModelTier, api_key: str | None):
        self.model_id = model_id
        self.provider = "openai"
        self.tier = tier
        self.supports_reference_images = False
        self._client = OpenAI(api_key=api_key) if api_key else None

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

        response = self._client.images.generate(
            model=self.model_id,
            prompt=final_prompt,
            size=_size_str(request.width, request.height),
        )
        response_data = response.data or []
        if not response_data:
            raise RuntimeError(f"No image payload returned for {self.model_id}")
        image_b64 = response_data[0].b64_json
        if image_b64 is None:
            raise RuntimeError(f"No image payload returned for {self.model_id}")
        image_bytes = base64.b64decode(image_b64)
        out_path = Path(request.output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image_bytes)
        usage: dict[str, Any] = {}
        if hasattr(response, "usage") and response.usage:
            usage = cast(dict[str, Any], response.usage.model_dump())
        return PanelImageResult(
            image_path=request.output_path,
            provider_usage=usage,
            estimated_cost_usd=estimate_cost(self.model_id, 1),
        )
