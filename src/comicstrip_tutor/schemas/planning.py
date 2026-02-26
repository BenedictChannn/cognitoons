"""Planning-related schema models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LearningPlan(BaseModel):
    """High-level teaching objectives and misconceptions."""

    topic: str
    audience_level: str = "beginner"
    objectives: list[str] = Field(default_factory=list, min_length=1)
    misconceptions: list[str] = Field(default_factory=list)
    recap_message: str


class StoryArc(BaseModel):
    """Comic narrative arc."""

    setup: str
    confusion: str
    insight: str
    recap: str


class CharacterProfile(BaseModel):
    """Recurring comic character."""

    name: str
    role: str
    personality: str
    visual_traits: list[str] = Field(default_factory=list, min_length=1)
