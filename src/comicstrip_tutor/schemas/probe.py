"""Schemas for model probe diagnostics."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ProbeAttempt(BaseModel):
    """Single probe attempt metadata."""

    attempt: int = Field(ge=1)
    success: bool
    latency_s: float
    error_type: str | None = None
    error_message: str | None = None
    provider_usage: dict[str, Any] = Field(default_factory=dict)
    image_path: str | None = None


class ModelProbeResult(BaseModel):
    """Aggregate probe run output."""

    probe_id: str
    model_key: str
    prompt: str
    repetitions: int = Field(ge=1)
    width: int = Field(ge=64)
    height: int = Field(ge=64)
    dry_run: bool = False
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    attempts: list[ProbeAttempt] = Field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
