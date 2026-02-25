"""Provider-agnostic image model interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

ModelTier = Literal["cheap", "mid", "premium"]


@dataclass(slots=True)
class PanelImageRequest:
    """Unified panel image generation request."""

    panel_number: int
    prompt: str
    width: int
    height: int
    style_guide: str
    output_path: str
    seed: int | None = None
    reference_image_paths: list[str] = field(default_factory=list)
    dry_run: bool = False


@dataclass(slots=True)
class PanelImageResult:
    """Unified model output."""

    image_path: str
    provider_usage: dict[str, Any]
    estimated_cost_usd: float


class ImageModel(ABC):
    """Image model adapter interface."""

    model_id: str
    provider: str
    tier: ModelTier
    supports_reference_images: bool = False

    @abstractmethod
    def generate_panel_image(self, request: PanelImageRequest) -> PanelImageResult:
        """Generate a panel image for the supplied prompt."""
