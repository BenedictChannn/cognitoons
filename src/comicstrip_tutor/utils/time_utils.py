"""Time helpers."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_timestamp() -> str:
    """UTC timestamp for IDs and logging."""
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
