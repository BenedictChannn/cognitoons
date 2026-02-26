"""Exploration arm ID helpers."""

from __future__ import annotations


def build_arm_id(*, template: str, theme: str, model_key: str, image_text_mode: str) -> str:
    """Build canonical arm identifier used by exploration bandit."""
    return f"{template}|{theme}|{model_key}|{image_text_mode}"
