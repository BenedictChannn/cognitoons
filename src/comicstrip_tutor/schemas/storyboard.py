"""Storyboard schema."""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class PanelScript(BaseModel):
    """Single panel script with teaching intent."""

    panel_number: int = Field(ge=1)
    scene_description: str = Field(min_length=10)
    dialogue_or_caption: str = Field(min_length=5)
    teaching_intent: str = Field(min_length=5)
    misconception_addressed: str | None = None
    expected_takeaway: str | None = None
    metaphor_anchor: str | None = None


class Storyboard(BaseModel):
    """Storyboard for a whole comic strip."""

    topic: str
    audience_level: str = "beginner"
    story_title: str
    character_style_guide: str
    recurring_characters: list[str] = Field(min_length=2)
    panels: list[PanelScript] = Field(min_length=4, max_length=12)
    recap_panel: int | None = None

    @field_validator("recap_panel")
    @classmethod
    def validate_recap_panel(cls, recap_panel: int | None, info: ValidationInfo) -> int | None:
        if recap_panel is None:
            return recap_panel
        panels = info.data.get("panels", [])
        if panels and (recap_panel < 1 or recap_panel > len(panels)):
            raise ValueError("recap_panel must be within panel index range")
        return recap_panel
