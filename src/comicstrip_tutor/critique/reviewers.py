"""Persona-based storyboard critique reviewers."""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz.fuzz import token_set_ratio

from comicstrip_tutor.composition.text_layout import layout_caption
from comicstrip_tutor.schemas.critique import CritiqueIssue, ReviewerCritique
from comicstrip_tutor.schemas.storyboard import Storyboard

_TECHNICAL_TERMS = {
    "tradeoff",
    "estimate",
    "exploration",
    "exploitation",
    "policy",
    "gradient",
    "consistency",
    "throughput",
    "latency",
    "value",
    "reward",
}
_BEGINNER_JARGON = {
    "stochastic",
    "bellman",
    "eigenvector",
    "backprop",
    "liveness",
    "quorum",
    "idempotency",
}


@dataclass(slots=True)
class CritiqueContext:
    """Common context shared by critique reviewers."""

    expected_key_points: list[str]
    misconceptions: list[str]
    audience_level: str


def _script_corpus(storyboard: Storyboard) -> str:
    return " ".join(
        f"{panel.scene_description} {panel.dialogue_or_caption} {panel.teaching_intent}"
        for panel in storyboard.panels
    )


def technical_reviewer(storyboard: Storyboard, context: CritiqueContext) -> ReviewerCritique:
    """Check factual coverage and misconception handling proxies."""
    issues: list[CritiqueIssue] = []
    corpus = _script_corpus(storyboard).lower()

    for point in context.expected_key_points:
        match = token_set_ratio(point.lower(), corpus)
        if match < 45:
            issues.append(
                CritiqueIssue(
                    reviewer="technical",
                    severity="critical",
                    message=f"Expected key point missing or too weak: '{point}'",
                    recommendation=f"Add explicit panel teaching intent for '{point}'.",
                )
            )

    if context.misconceptions:
        misconception_hits = 0
        for misconception in context.misconceptions:
            if token_set_ratio(misconception.lower(), corpus) > 35:
                misconception_hits += 1
        if misconception_hits == 0:
            issues.append(
                CritiqueIssue(
                    reviewer="technical",
                    severity="major",
                    message="Storyboard does not explicitly address listed misconceptions.",
                    recommendation="Add at least one panel that debunks a common misconception.",
                )
            )

    term_hits = sum(term in corpus for term in _TECHNICAL_TERMS)
    if term_hits < 2:
        issues.append(
            CritiqueIssue(
                reviewer="technical",
                severity="major",
                message="Technical rigor appears low (few concrete technical concepts).",
                recommendation="Add explicit tradeoff/formal concept language in teaching intents.",
            )
        )

    score = max(
        0.0,
        1.0
        - (0.25 * sum(issue.severity == "critical" for issue in issues))
        - (0.1 * sum(issue.severity == "major" for issue in issues)),
    )
    verdict = "fail" if any(issue.severity == "critical" for issue in issues) else "pass"
    return ReviewerCritique(
        reviewer="technical",
        verdict=verdict,
        score=round(score, 4),
        confidence=0.78,
        summary="Validated technical key-point coverage and misconception handling.",
        issues=issues,
    )


def beginner_reviewer(storyboard: Storyboard, context: CritiqueContext) -> ReviewerCritique:
    """Check beginner readability and jargon load."""
    issues: list[CritiqueIssue] = []
    captions = [panel.dialogue_or_caption for panel in storyboard.panels]
    words = " ".join(captions).lower().split()
    avg_words_per_caption = sum(len(caption.split()) for caption in captions) / max(
        1, len(captions)
    )
    jargon_hits = sum(token in _BEGINNER_JARGON for token in words)

    if avg_words_per_caption > 34:
        issues.append(
            CritiqueIssue(
                reviewer="beginner",
                severity="major",
                message="Dialogue is too dense for beginner reader.",
                recommendation="Shorten caption text and split dense ideas across panels.",
            )
        )
    if jargon_hits > 3 and context.audience_level == "beginner":
        issues.append(
            CritiqueIssue(
                reviewer="beginner",
                severity="major",
                message="Too much unexplained jargon for beginner audience.",
                recommendation=(
                    "Introduce jargon only after intuitive explanation or add quick definitions."
                ),
            )
        )

    metaphor_panels = sum(1 for panel in storyboard.panels if panel.metaphor_anchor)
    if metaphor_panels == 0:
        issues.append(
            CritiqueIssue(
                reviewer="beginner",
                severity="minor",
                message="No metaphor anchors detected for digestibility.",
                recommendation=(
                    "Add at least one concrete metaphor anchor in confusion/insight panels."
                ),
            )
        )

    score = max(0.0, 1.0 - (0.12 * len(issues)))
    verdict = "pass" if all(issue.severity != "major" for issue in issues) else "fail"
    return ReviewerCritique(
        reviewer="beginner",
        verdict=verdict,
        score=round(score, 4),
        confidence=0.74,
        summary="Evaluated readability, jargon burden, and metaphor support.",
        issues=issues,
    )


def first_year_reviewer(storyboard: Storyboard, _: CritiqueContext) -> ReviewerCritique:
    """Check bridge between intuition and formalism."""
    issues: list[CritiqueIssue] = []
    corpus = _script_corpus(storyboard).lower()
    has_intuition = any(token in corpus for token in {"intuition", "metaphor", "imagine", "story"})
    has_formal = any(
        token in corpus for token in {"formula", "estimate", "value", "policy", "tradeoff"}
    )

    if not (has_intuition and has_formal):
        issues.append(
            CritiqueIssue(
                reviewer="first_year",
                severity="major",
                message="Insufficient bridge between intuitive and formal explanation layers.",
                recommendation=(
                    "Add at least one panel linking metaphor intuition to formal decision rule."
                ),
            )
        )

    score = 0.9 if not issues else 0.65
    return ReviewerCritique(
        reviewer="first_year",
        verdict="pass" if not issues else "fail",
        score=score,
        confidence=0.71,
        summary="Checked intuition-to-formalism bridge quality.",
        issues=issues,
    )


def pedagogy_reviewer(storyboard: Storyboard, _: CritiqueContext) -> ReviewerCritique:
    """Check narrative teaching arc structure."""
    issues: list[CritiqueIssue] = []
    if storyboard.recap_panel != len(storyboard.panels):
        issues.append(
            CritiqueIssue(
                reviewer="pedagogy",
                severity="critical",
                message="Recap panel is not configured as the final panel.",
                recommendation="Ensure recap panel index is the last panel.",
            )
        )
    if len(storyboard.panels) < 4:
        issues.append(
            CritiqueIssue(
                reviewer="pedagogy",
                severity="critical",
                message="Panel count too low for proper setup/confusion/insight/recap arc.",
                recommendation="Use at least 4 panels for pedagogical progression.",
            )
        )
    if not any("confusion" in panel.scene_description.lower() for panel in storyboard.panels):
        issues.append(
            CritiqueIssue(
                reviewer="pedagogy",
                severity="major",
                message="No explicit confusion moment detected.",
                recommendation="Add a panel where naive understanding fails before insight.",
            )
        )

    score = max(
        0.0,
        1.0
        - (0.25 * sum(issue.severity == "critical" for issue in issues))
        - (0.1 * sum(issue.severity == "major" for issue in issues)),
    )
    verdict = "fail" if any(issue.severity == "critical" for issue in issues) else "pass"
    return ReviewerCritique(
        reviewer="pedagogy",
        verdict=verdict,
        score=round(score, 4),
        confidence=0.8,
        summary="Validated narrative progression for teaching effectiveness.",
        issues=issues,
    )


def visual_reviewer(storyboard: Storyboard, _: CritiqueContext) -> ReviewerCritique:
    """Check readability and text density constraints for visual flow."""
    issues: list[CritiqueIssue] = []
    for panel in storyboard.panels:
        layout = layout_caption(panel.dialogue_or_caption, max_chars_per_line=44, max_lines=4)
        if layout.overflow:
            issues.append(
                CritiqueIssue(
                    reviewer="visual",
                    severity="major",
                    panel_number=panel.panel_number,
                    message="Caption overflow risk detected for panel.",
                    recommendation="Reduce caption length or split into two panels.",
                )
            )
        if len(panel.dialogue_or_caption) > 280:
            issues.append(
                CritiqueIssue(
                    reviewer="visual",
                    severity="major",
                    panel_number=panel.panel_number,
                    message="Caption too long for readable comic panel.",
                    recommendation="Keep panel dialogue concise and focused.",
                )
            )
    score = max(0.0, 1.0 - (0.1 * len(issues)))
    verdict = "pass" if not issues else "fail"
    return ReviewerCritique(
        reviewer="visual",
        verdict=verdict,
        score=round(score, 4),
        confidence=0.77,
        summary="Checked caption density and readability safety constraints.",
        issues=issues,
    )
