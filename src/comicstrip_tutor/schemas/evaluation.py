"""Evaluation schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationMetricSet(BaseModel):
    """Comic rubric metric scores in [0,1]."""

    concept_coverage: float = Field(ge=0, le=1)
    coherence: float = Field(ge=0, le=1)
    visual_text_alignment: float = Field(ge=0, le=1)
    readability: float = Field(ge=0, le=1)
    consistency: float = Field(ge=0, le=1)
    llm_judge: float | None = Field(default=None, ge=0, le=1)

    @property
    def aggregate(self) -> float:
        base = [
            self.concept_coverage,
            self.coherence,
            self.visual_text_alignment,
            self.readability,
            self.consistency,
        ]
        if self.llm_judge is not None:
            return round(sum(base + [self.llm_judge]) / 6.0, 4)
        return round(sum(base) / 5.0, 4)


class EvaluationResult(BaseModel):
    """Saved evaluation result."""

    run_id: str
    model_key: str
    metrics: EvaluationMetricSet
    comprehension_score: float | None = Field(default=None, ge=0, le=1)
    technical_rigor_score: float | None = Field(default=None, ge=0, le=1)
    learning_effectiveness_score: float | None = Field(default=None, ge=0, le=1)
    publishable: bool = False
    publishable_reasons: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
