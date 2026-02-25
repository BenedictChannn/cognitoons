"""Build per-panel image prompts with consistency injection."""

from __future__ import annotations

from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def build_panel_prompt(storyboard: Storyboard, panel: PanelScript) -> str:
    """Build image prompt from storyboard panel."""
    metaphor = f"\nMetaphor anchor: {panel.metaphor_anchor}" if panel.metaphor_anchor else ""
    recurring = ", ".join(storyboard.recurring_characters)
    return (
        f"Title: {storyboard.story_title}\n"
        f"Topic: {storyboard.topic}\n"
        f"Audience: {storyboard.audience_level}\n"
        f"Recurring characters: {recurring}\n"
        f"Style and consistency guide: {storyboard.character_style_guide}\n"
        f"Scene: {panel.scene_description}\n"
        f"Dialogue text to make legible in scene: {panel.dialogue_or_caption}\n"
        f"Teaching intent: {panel.teaching_intent}{metaphor}\n"
        "Instructions: keep characters visually consistent with prior panels."
    )
