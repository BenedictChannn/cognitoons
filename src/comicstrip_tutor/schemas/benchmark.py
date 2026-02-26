"""Benchmark schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkItem(BaseModel):
    """Dataset row for model benchmark."""

    id: str
    topic: str
    audience_level: str = "beginner"
    expected_key_points: list[str] = Field(default_factory=list, min_length=1)
    common_misconceptions: list[str] = Field(default_factory=list)


class BenchmarkModelResult(BaseModel):
    """Single item result for one model."""

    item_id: str
    model_key: str
    score: float = Field(ge=0, le=1)
    learning_effectiveness_score: float | None = Field(default=None, ge=0, le=1)
    comprehension_score: float | None = Field(default=None, ge=0, le=1)
    technical_rigor_score: float | None = Field(default=None, ge=0, le=1)
    publishable: bool = False
    cost_usd: float = Field(ge=0, default=0)
    run_id: str


class BenchmarkRunResult(BaseModel):
    """Whole benchmark run result."""

    benchmark_id: str
    model_results: list[BenchmarkModelResult] = Field(default_factory=list)
    leaderboard: list[dict[str, float | str]] = Field(default_factory=list)
