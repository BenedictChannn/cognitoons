"""Fallback synthetic rendering for dry-run and tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import fill

from PIL import Image, ImageDraw, ImageFont


def create_placeholder_image(
    output_path: str,
    title: str,
    prompt: str,
    width: int,
    height: int,
) -> None:
    """Create synthetic image with readable prompt text."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (width, height), color=(246, 247, 252))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((10, 10, width - 10, height - 10), outline=(50, 50, 50), width=3)
    draw.text((24, 24), title, fill=(24, 24, 24), font=font)
    draw.text((24, 56), fill(prompt, width=45), fill=(35, 35, 35), font=font)
    image.save(path, format="PNG")
