"""Storyboard-first planner for technical comics."""

from __future__ import annotations

from dataclasses import dataclass

from comicstrip_tutor.schemas.planning import CharacterProfile, LearningPlan, StoryArc
from comicstrip_tutor.schemas.storyboard import PanelScript, Storyboard
from comicstrip_tutor.styles.compiler import compile_style_guide


@dataclass(slots=True)
class PlanningBundle:
    """All explicit intermediate planning artifacts."""

    learning_plan: LearningPlan
    story_arc: StoryArc
    characters: list[CharacterProfile]
    storyboard: Storyboard


def _extract_points(text: str, max_points: int = 5) -> list[str]:
    chunks = [chunk.strip(" .") for chunk in text.replace("\n", " ").split(",")]
    points = [chunk for chunk in chunks if len(chunk) > 12]
    if not points:
        return [f"Core idea of {text}", f"Why {text} matters", f"How to apply {text}"]
    return points[:max_points]


def build_plan(
    *,
    topic: str | None,
    source_text: str | None,
    panel_count: int,
    audience_level: str,
    template: str = "intuition-to-formalism",
    theme: str = "clean-whiteboard",
) -> PlanningBundle:
    """Build learning plan + storyboard from input topic/source."""
    subject = topic or "Source content"
    base_text = source_text or topic or "technical concept"
    key_points = _extract_points(base_text)
    misconceptions = [
        f"{subject} has only one correct strategy",
        f"{subject} is purely theoretical and not practical",
    ]
    learning_plan = LearningPlan(
        topic=subject,
        audience_level=audience_level,
        objectives=[
            f"Understand the intuition behind {subject}",
            f"Explain {subject} with a simple metaphor",
            f"Apply {subject} to a practical engineering decision",
        ],
        misconceptions=misconceptions,
        recap_message=f"{subject}: balance intuition, structure, and tradeoffs.",
    )
    story_arc = StoryArc(
        setup=f"Characters encounter a real problem requiring {subject}.",
        confusion="They choose a naive strategy and hit failure.",
        insight="They discover a better mental model and improve outcomes.",
        recap=f"They summarize {subject} as a repeatable decision process.",
    )
    characters = [
        CharacterProfile(
            name="Ada",
            role="curious engineer",
            personality="analytical and practical",
            visual_traits=["short blue hair", "hoodie", "notebook"],
        ),
        CharacterProfile(
            name="Turing",
            role="mentor engineer",
            personality="calm and metaphor-driven",
            visual_traits=["round glasses", "green jacket", "marker pen"],
        ),
    ]
    style_guide = compile_style_guide(
        template_id=template,
        theme_id=theme,
        audience_level=audience_level,
    )
    beat_hints = style_guide.template.beat_hints
    panels: list[PanelScript] = []
    for idx in range(panel_count):
        if idx == panel_count - 1:
            arc_step = "recap"
        elif idx == 0:
            arc_step = beat_hints[0]
        elif idx == 1:
            arc_step = beat_hints[1]
        elif idx == 2:
            arc_step = beat_hints[2]
        else:
            arc_step = "insight"
        point = key_points[idx % len(key_points)]
        panels.append(
            PanelScript(
                panel_number=idx + 1,
                scene_description=(
                    f"{arc_step.title()} scene ({style_guide.template.title}): "
                    f"Ada and Turing discuss {point}."
                ),
                dialogue_or_caption=(
                    f'Ada: "I thought {subject} was simpler." '
                    f'Turing: "Let’s unpack {point} with a metaphor."'
                ),
                teaching_intent=f"Teach: {point}",
                misconception_addressed=misconceptions[idx % len(misconceptions)]
                if misconceptions
                else None,
                expected_takeaway=f"After this panel, learner understands: {point}.",
                metaphor_anchor="Exploring hallways with a map and scorecard"
                if arc_step in {"confusion", "insight"}
                else None,
            )
        )
    storyboard = Storyboard(
        topic=subject,
        audience_level=audience_level,
        template=style_guide.template.template_id,
        theme=style_guide.theme.theme_id,
        story_title=f"{subject}: A Visual Walkthrough ({template}, {theme})",
        character_style_guide=style_guide.style_text,
        recurring_characters=[character.name for character in characters],
        panels=panels,
        recap_panel=panel_count,
    )
    return PlanningBundle(
        learning_plan=learning_plan,
        story_arc=story_arc,
        characters=characters,
        storyboard=storyboard,
    )
