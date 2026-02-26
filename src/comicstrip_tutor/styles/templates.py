"""Pedagogical template registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TemplateSpec:
    """Narrative pedagogy template specification."""

    template_id: str
    title: str
    description: str
    beat_hints: tuple[str, ...]
    instruction: str


TEMPLATE_REGISTRY: dict[str, TemplateSpec] = {
    "misconception-first": TemplateSpec(
        template_id="misconception-first",
        title="Misconception First",
        description="Start from a common wrong idea, then fix it progressively.",
        beat_hints=("myth", "failure", "correction", "recap"),
        instruction=(
            "Lead with a realistic misconception and explicitly show why it fails "
            "before introducing the correct model."
        ),
    ),
    "intuition-to-formalism": TemplateSpec(
        template_id="intuition-to-formalism",
        title="Intuition to Formalism",
        description="Build intuitive metaphor first, then connect to formal rule.",
        beat_hints=("intuition", "confusion", "formal-rule", "recap"),
        instruction=(
            "Translate intuitive framing into technical terms by panel 3, and recap the mapping."
        ),
    ),
    "worked-example-driven": TemplateSpec(
        template_id="worked-example-driven",
        title="Worked Example",
        description="Walk through a concrete example from start to finish.",
        beat_hints=("problem", "attempt", "step-through", "recap"),
        instruction="Keep each panel tied to a concrete state transition in one worked example.",
    ),
    "failure-postmortem": TemplateSpec(
        template_id="failure-postmortem",
        title="Failure Postmortem",
        description="Analyze a failure incident to derive the core concept.",
        beat_hints=("incident", "root-cause", "fix", "recap"),
        instruction=(
            "Use incident -> root-cause -> remediation progression with explicit lesson learned."
        ),
    ),
    "compare-and-contrast": TemplateSpec(
        template_id="compare-and-contrast",
        title="Compare and Contrast",
        description="Compare naive and robust strategies side by side.",
        beat_hints=("naive-path", "robust-path", "tradeoff", "recap"),
        instruction="Highlight tradeoffs between two strategies and when each is appropriate.",
    ),
}


def list_templates() -> list[TemplateSpec]:
    """Return all registered template specs."""
    return list(TEMPLATE_REGISTRY.values())
