"""Visual and narrative theme registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ThemeSpec:
    """Visual theme specification."""

    theme_id: str
    title: str
    description: str
    visual_style: str
    tone: str
    palette: tuple[str, ...]


THEME_REGISTRY: dict[str, ThemeSpec] = {
    "clean-whiteboard": ThemeSpec(
        theme_id="clean-whiteboard",
        title="Clean Whiteboard",
        description="Minimal educational visual style with high readability.",
        visual_style="clean white background, crisp lines, clear spacing",
        tone="calm and explanatory",
        palette=("white", "charcoal", "blue"),
    ),
    "sci-fi-lab": ThemeSpec(
        theme_id="sci-fi-lab",
        title="Sci-Fi Lab",
        description="Future lab metaphor with neon accents and instrumentation.",
        visual_style="futuristic lab environment with glowing UI elements",
        tone="curious and experimental",
        palette=("midnight", "cyan", "violet"),
    ),
    "playful-manga-lite": ThemeSpec(
        theme_id="playful-manga-lite",
        title="Playful Manga-Lite",
        description="Expressive, dynamic framing while preserving readability.",
        visual_style="light manga-inspired expressions and dynamic panel angles",
        tone="energetic and approachable",
        palette=("cream", "black", "coral"),
    ),
    "textbook-modern": ThemeSpec(
        theme_id="textbook-modern",
        title="Textbook Modern",
        description="Infographic-like technical clarity with comic narrative.",
        visual_style="modern textbook diagram elements integrated into scenes",
        tone="precise and instructional",
        palette=("offwhite", "navy", "teal"),
    ),
    "retro-terminal": ThemeSpec(
        theme_id="retro-terminal",
        title="Retro Terminal",
        description="Nostalgic terminal-era visuals for systems concepts.",
        visual_style="retro terminal motifs with geometric overlays",
        tone="analytical and slightly nostalgic",
        palette=("black", "green", "amber"),
    ),
}


def list_themes() -> list[ThemeSpec]:
    """Return all registered themes."""
    return list(THEME_REGISTRY.values())
