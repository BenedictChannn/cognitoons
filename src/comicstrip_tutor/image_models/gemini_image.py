"""Gemini image adapter."""

from __future__ import annotations

import base64
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

    def _usage_dict(self, response: Any) -> dict[str, Any]:
        usage_metadata = getattr(response, "usage_metadata", None)
        if not usage_metadata:
            return {}
        if hasattr(usage_metadata, "model_dump"):
            return cast(dict[str, Any], usage_metadata.model_dump())
        if isinstance(usage_metadata, dict):
            return usage_metadata
        return {"usage_metadata": str(usage_metadata)}

    def _extract_inline_image_bytes(self, response: Any) -> bytes:
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                inline_data = getattr(part, "inline_data", None)
                if inline_data is None:
                    continue
                data = getattr(inline_data, "data", None)
                if isinstance(data, bytes):
                    return data
                if isinstance(data, str) and data:
                    return base64.b64decode(data)
        raise RuntimeError(f"No inline image data returned for {self.model_id}")

    def _generate_with_imagen_predict(self, final_prompt: str) -> tuple[bytes, dict[str, Any]]:
        if self._client is None:
            raise RuntimeError("Gemini client not initialized")
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
        return image_bytes, self._usage_dict(response)

    def _generate_with_gemini_content(self, final_prompt: str) -> tuple[bytes, dict[str, Any]]:
        if self._client is None:
            raise RuntimeError("Gemini client not initialized")
        response = self._client.models.generate_content(
            model=self.model_id,
            contents=final_prompt,
            config={"response_modalities": ["IMAGE"]},
        )
        return self._extract_inline_image_bytes(response), self._usage_dict(response)

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

        if self.model_id.startswith("imagen-"):
            image_bytes, usage = self._generate_with_imagen_predict(final_prompt)
        else:
            image_bytes, usage = self._generate_with_gemini_content(final_prompt)
        out_path = Path(request.output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image_bytes)
        return PanelImageResult(
            image_path=request.output_path,
            provider_usage=usage,
            estimated_cost_usd=estimate_cost(self.model_id, 1),
        )
