"""Critique and review schema models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from comicstrip_tutor.schemas.runs import CritiqueMode

Severity = Literal["critical", "major", "minor"]
Verdict = Literal["pass", "fail"]


class CritiqueIssue(BaseModel):
    """Single issue raised by a critique reviewer."""

    reviewer: str
    severity: Severity
    message: str
    recommendation: str
    panel_number: int | None = None


class ReviewerCritique(BaseModel):
    """Structured output from one reviewer persona."""

    reviewer: str
    verdict: Verdict
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    summary: str
    issues: list[CritiqueIssue] = Field(default_factory=list)


class CritiqueReport(BaseModel):
    """Aggregated critique report used for gating."""

    run_id: str
    stage: str
    critique_mode: CritiqueMode
    overall_verdict: Verdict
    overall_score: float = Field(ge=0, le=1)
    blocking_issue_count: int = 0
    major_issue_count: int = 0
    reviewer_reports: list[ReviewerCritique] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
