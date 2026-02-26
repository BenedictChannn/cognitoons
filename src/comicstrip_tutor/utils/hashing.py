"""Hashing helpers."""

from __future__ import annotations

import hashlib


def sha256_text(value: str) -> str:
    """Compute SHA-256 hash hex digest for text."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
