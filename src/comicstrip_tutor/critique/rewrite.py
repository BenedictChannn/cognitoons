"""Heuristic critique-driven storyboard rewrite helpers."""

from __future__ import annotations

import re

from comicstrip_tutor.schemas.critique import CritiqueReport
from comicstrip_tutor.schemas.storyboard import Storyboard


def _normalize_space(text: str) -> str:
    return " ".join(text.split())


def _append_once(text: str, suffix: str) -> str:
    normalized = text.lower()
    if suffix.lower() in normalized:
        return text
    return _normalize_space(f"{text.rstrip()} {suffix.strip()}")


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "…"


def _critical_point_from_message(message: str) -> str | None:
    match = re.search(r"'([^']+)'", message)
    if match:
        return match.group(1)
    return None


def apply_targeted_rewrites(
    *,
    storyboard: Storyboard,
    critique_report: CritiqueReport,
    expected_key_points: list[str],
    misconceptions: list[str],
) -> tuple[Storyboard, list[str]]:
    """Apply deterministic storyboard rewrites based on critique output."""
    revised = storyboard.model_copy(deep=True)
    rewrite_notes: list[str] = []

    if revised.recap_panel != len(revised.panels):
        revised.recap_panel = len(revised.panels)
        rewrite_notes.append("Moved recap panel to final position.")

    all_issues = [issue for report in critique_report.reviewer_reports for issue in report.issues]
    if not all_issues:
        return revised, rewrite_notes

    if not any("confusion" in panel.scene_description.lower() for panel in revised.panels):
        target = revised.panels[min(1, len(revised.panels) - 1)]
        target.scene_description = _append_once(
            target.scene_description,
            "Confusion moment: naive approach fails and forces re-think.",
        )
        rewrite_notes.append("Added explicit confusion moment panel.")

    technical_panel = revised.panels[min(2, len(revised.panels) - 1)]
    bridge_suffix = (
        "Bridge intuition to formalism: choose action maximizing value estimate "
        "plus uncertainty bonus."
    )

    for issue in all_issues:
        message = issue.message.lower()
        recommendation = issue.recommendation.lower()

        if issue.reviewer == "technical" and "key point missing" in message:
            missing_point = _critical_point_from_message(issue.message)
            target_point = missing_point or (
                expected_key_points[0] if expected_key_points else "core concept"
            )
            technical_panel.teaching_intent = _append_once(
                technical_panel.teaching_intent,
                f"Explicit key point: {target_point}.",
            )
            technical_panel.expected_takeaway = _append_once(
                technical_panel.expected_takeaway or technical_panel.teaching_intent,
                f"Learner can explain {target_point}.",
            )
            rewrite_notes.append(f"Injected missing key point: {target_point}.")
            continue

        if "technical rigor appears low" in message or "formal concept" in recommendation:
            technical_panel.teaching_intent = _append_once(
                technical_panel.teaching_intent,
                "Formal tradeoff terms: policy, value estimate, and exploration bonus.",
            )
            rewrite_notes.append("Strengthened technical rigor language.")
            continue

        if issue.reviewer == "first_year" and "bridge" in message:
            technical_panel.teaching_intent = _append_once(
                technical_panel.teaching_intent,
                bridge_suffix,
            )
            rewrite_notes.append("Added intuition-to-formal bridge sentence.")
            continue

        if issue.reviewer == "beginner" and "too dense" in message:
            for panel in revised.panels:
                panel.dialogue_or_caption = _truncate_words(panel.dialogue_or_caption, max_words=24)
            rewrite_notes.append("Shortened dense dialogue for beginner readability.")
            continue

        if issue.reviewer == "visual" and issue.panel_number is not None:
            panel = next(
                (entry for entry in revised.panels if entry.panel_number == issue.panel_number),
                None,
            )
            if panel is not None:
                panel.dialogue_or_caption = _truncate_words(panel.dialogue_or_caption, max_words=22)
                rewrite_notes.append(f"Reduced caption overflow on panel {issue.panel_number}.")
            continue

    if misconceptions and any("misconception" in issue.message.lower() for issue in all_issues):
        for idx, panel in enumerate(revised.panels):
            panel.misconception_addressed = misconceptions[idx % len(misconceptions)]
        rewrite_notes.append("Mapped misconceptions explicitly across panels.")

    if (
        critique_report.major_issue_count > 2
        and revised.panels
        and revised.panels[-1].expected_takeaway is not None
    ):
        revised.panels[-1].expected_takeaway = _append_once(
            revised.panels[-1].expected_takeaway,
            "Final recap includes why naive strategy fails and when to apply the formal rule.",
        )
        rewrite_notes.append("Added stronger recap takeaway due to unresolved major issues.")

    return revised, list(dict.fromkeys(rewrite_notes))
