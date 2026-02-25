"""Heuristic scoring for comic outputs."""

from __future__ import annotations

from pathlib import Path

from rapidfuzz.fuzz import token_set_ratio

from comicstrip_tutor.composition.text_layout import layout_caption
from comicstrip_tutor.schemas.storyboard import Storyboard


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def concept_coverage(storyboard: Storyboard, expected_key_points: list[str]) -> float:
    """Fuzzy-match expected key points against teaching intents."""
    corpus = " ".join(panel.teaching_intent for panel in storyboard.panels)
    scores = [token_set_ratio(point, corpus) / 100 for point in expected_key_points]
    return round(_avg(scores), 4)


def coherence(storyboard: Storyboard) -> float:
    """Simple narrative continuity check."""
    panel_numbers = [panel.panel_number for panel in storyboard.panels]
    ascending = panel_numbers == sorted(panel_numbers)
    has_recap = storyboard.recap_panel == len(storyboard.panels)
    return 1.0 if (ascending and has_recap) else 0.7


def visual_text_alignment(storyboard: Storyboard) -> float:
    """Checks overlap between scene and dialogue terms."""
    panel_scores: list[float] = []
    for panel in storyboard.panels:
        panel_scores.append(
            token_set_ratio(panel.scene_description, panel.dialogue_or_caption) / 100
        )
    return round(_avg(panel_scores), 4)


def readability(storyboard: Storyboard) -> float:
    """Caption readability score from line wrapping overflow."""
    overflows = 0
    for panel in storyboard.panels:
        if layout_caption(panel.dialogue_or_caption).overflow:
            overflows += 1
    ratio = 1.0 - (overflows / len(storyboard.panels))
    return round(max(0.0, ratio), 4)


def consistency(storyboard: Storyboard, prompt_paths: list[Path]) -> float:
    """Character/style consistency score based on prompt coverage."""
    text_blob = " ".join(path.read_text(encoding="utf-8") for path in prompt_paths if path.exists())
    hits = 0
    for character in storyboard.recurring_characters:
        if character.lower() in text_blob.lower():
            hits += 1
    char_score = hits / max(1, len(storyboard.recurring_characters))
    style_score = 1.0 if storyboard.character_style_guide.lower()[:20] in text_blob.lower() else 0.7
    return round((char_score + style_score) / 2.0, 4)


def heuristic_checks(storyboard: Storyboard, image_paths: list[Path]) -> dict[str, bool]:
    """Boolean checks required for rubric sanity."""
    return {
        "panel_count_valid": 4 <= len(storyboard.panels) <= 12,
        "captions_non_empty": all(panel.dialogue_or_caption.strip() for panel in storyboard.panels),
        "images_exist": all(path.exists() for path in image_paths),
        "recap_present": storyboard.recap_panel == len(storyboard.panels),
    }
