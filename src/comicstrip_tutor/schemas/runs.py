"""Run-level schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RunMode = Literal["draft", "publish"]


class RunConfig(BaseModel):
    """Input config saved for reproducibility."""

    run_id: str
    topic: str | None = None
    source_text: str | None = None
    audience_level: str = "beginner"
    panel_count: int = Field(ge=4, le=12, default=6)
    mode: RunMode = "draft"
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class PanelRenderRecord(BaseModel):
    """Per-panel render record."""

    panel_number: int
    prompt_path: str
    image_path: str
    estimated_cost_usd: float = 0.0
    provider_usage: dict[str, Any] = Field(default_factory=dict)


class RenderRunManifest(BaseModel):
    """Manifest for model-specific render run."""

    run_id: str
    model_key: str
    provider: str
    mode: RunMode
    storyboard_hash: str
    prompt_hash: str
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    panel_records: list[PanelRenderRecord] = Field(default_factory=list)
    total_estimated_cost_usd: float = 0.0
    notes: list[str] = Field(default_factory=list)


class CompareRunSummary(BaseModel):
    """Summary for side-by-side model comparison."""

    run_id: str
    model_a: str
    model_b: str
    output_path: str
