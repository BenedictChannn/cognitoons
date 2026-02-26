"""Product presets for onboarding and repeatable workflows."""

from __future__ import annotations

from dataclasses import dataclass

from comicstrip_tutor.schemas.runs import CritiqueMode, ImageTextMode, RunMode


@dataclass(slots=True, frozen=True)
class RunPreset:
    """Preset configuration for common workflows."""

    preset_id: str
    description: str
    panel_count: int
    mode: RunMode
    critique_mode: CritiqueMode
    auto_rewrite: bool
    critique_max_iterations: int
    image_text_mode: ImageTextMode
    template: str
    theme: str


PRESET_REGISTRY: dict[str, RunPreset] = {
    "fast-draft": RunPreset(
        preset_id="fast-draft",
        description="Low-friction draft for quick iteration.",
        panel_count=4,
        mode="draft",
        critique_mode="warn",
        auto_rewrite=True,
        critique_max_iterations=1,
        image_text_mode="none",
        template="intuition-to-formalism",
        theme="clean-whiteboard",
    ),
    "publish-strict": RunPreset(
        preset_id="publish-strict",
        description="Strict publish-quality setup with stronger critique loop.",
        panel_count=6,
        mode="publish",
        critique_mode="strict",
        auto_rewrite=True,
        critique_max_iterations=4,
        image_text_mode="none",
        template="misconception-first",
        theme="textbook-modern",
    ),
    "cost-aware-explore": RunPreset(
        preset_id="cost-aware-explore",
        description="Cost-aware experimentation preset for cheap-tier exploration.",
        panel_count=4,
        mode="draft",
        critique_mode="warn",
        auto_rewrite=True,
        critique_max_iterations=2,
        image_text_mode="none",
        template="compare-and-contrast",
        theme="clean-whiteboard",
    ),
}


def get_preset(preset_id: str) -> RunPreset:
    """Fetch preset by ID."""
    if preset_id not in PRESET_REGISTRY:
        available = ", ".join(sorted(PRESET_REGISTRY))
        raise KeyError(f"Unknown preset '{preset_id}'. Available: {available}")
    return PRESET_REGISTRY[preset_id]


def list_presets() -> list[RunPreset]:
    """List all presets."""
    return list(PRESET_REGISTRY.values())
