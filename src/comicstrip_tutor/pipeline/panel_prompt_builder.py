"""Build per-panel image prompts with consistency injection."""

from __future__ import annotations

from comicstrip_tutor.schemas.runs import ImageTextMode
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard


def _text_rendering_instruction(image_text_mode: ImageTextMode, panel: PanelScript) -> str:
    if image_text_mode == "none":
        return (
            "Text policy: do NOT render speech bubbles, captions, labels, "
            "or any visible text in the image. "
            "Leave clean space for post-render typography overlays."
        )
    if image_text_mode == "minimal":
        return (
            "Text policy: render at most a tiny on-object label if absolutely necessary. "
            "Avoid long captions and speech bubbles."
        )
    return (
        "Text policy: include concise in-panel text and speech bubbles where useful. "
        f"Primary dialogue: {panel.dialogue_or_caption}"
    )


def build_panel_prompt(
    storyboard: Storyboard,
    panel: PanelScript,
    image_text_mode: ImageTextMode = "none",
) -> str:
    """Build image prompt from storyboard panel."""
    metaphor = f"\nMetaphor anchor: {panel.metaphor_anchor}" if panel.metaphor_anchor else ""
    recurring = ", ".join(storyboard.recurring_characters)
    text_instruction = _text_rendering_instruction(image_text_mode, panel)
    return (
        f"Title: {storyboard.story_title}\n"
        f"Topic: {storyboard.topic}\n"
        f"Audience: {storyboard.audience_level}\n"
        f"Recurring characters: {recurring}\n"
        f"Style and consistency guide: {storyboard.character_style_guide}\n"
        f"Scene: {panel.scene_description}\n"
        f"Dialogue text reference: {panel.dialogue_or_caption}\n"
        f"Teaching intent: {panel.teaching_intent}{metaphor}\n"
        f"Misconception addressed: {panel.misconception_addressed or 'none'}\n"
        f"Expected learner takeaway: {panel.expected_takeaway or panel.teaching_intent}\n"
        f"{text_instruction}\n"
        "Instructions: keep characters visually consistent with prior panels."
    )
