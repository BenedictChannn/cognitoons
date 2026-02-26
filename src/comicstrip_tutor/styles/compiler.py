"""Style-guide compiler for template+theme+audience."""

from __future__ import annotations

from dataclasses import dataclass

from comicstrip_tutor.styles.templates import TEMPLATE_REGISTRY, TemplateSpec
from comicstrip_tutor.styles.themes import THEME_REGISTRY, ThemeSpec


@dataclass(slots=True, frozen=True)
class CompiledStyleGuide:
    """Compiled style guide consumed by planner and renderer."""

    template: TemplateSpec
    theme: ThemeSpec
    audience_level: str
    visual_instruction: str
    pedagogy_instruction: str
    style_text: str


def compile_style_guide(
    *, template_id: str, theme_id: str, audience_level: str
) -> CompiledStyleGuide:
    """Compile style constraints from template and theme registries."""
    template = TEMPLATE_REGISTRY.get(template_id, TEMPLATE_REGISTRY["intuition-to-formalism"])
    theme = THEME_REGISTRY.get(theme_id, THEME_REGISTRY["clean-whiteboard"])
    visual_instruction = (
        f"Theme {theme.title}: {theme.visual_style}. Palette: {', '.join(theme.palette)}."
    )
    pedagogy_instruction = (
        f"Template {template.title}: {template.instruction} "
        f"Beats: {', '.join(template.beat_hints)}."
    )
    style_text = (
        f"{visual_instruction} Tone: {theme.tone}. Audience level: {audience_level}. "
        f"{pedagogy_instruction}"
    )
    return CompiledStyleGuide(
        template=template,
        theme=theme,
        audience_level=audience_level,
        visual_instruction=visual_instruction,
        pedagogy_instruction=pedagogy_instruction,
        style_text=style_text,
    )
