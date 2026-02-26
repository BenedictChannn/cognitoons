"""Text layout helpers for panel captions."""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import wrap


@dataclass(slots=True)
class TextLayoutResult:
    """Text layout result for readability checking."""

    wrapped_lines: list[str]
    min_font_size_pass: bool
    overflow: bool


def layout_caption(
    caption: str, max_chars_per_line: int = 42, max_lines: int = 5
) -> TextLayoutResult:
    """Wrap caption text and expose readability flags."""
    lines = wrap(caption.strip(), width=max_chars_per_line) or [caption.strip()]
    overflow = len(lines) > max_lines
    if overflow:
        lines = lines[:max_lines]
    return TextLayoutResult(
        wrapped_lines=lines,
        min_font_size_pass=True,
        overflow=overflow,
    )
