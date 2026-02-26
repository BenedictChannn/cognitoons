"""Compose panel images into comic strips."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comicstrip_tutor.composition.text_layout import layout_caption
from comicstrip_tutor.schemas.storyboard import Storyboard


def compose_strip(
    *,
    storyboard: Storyboard,
    panel_image_paths: list[str],
    output_png: Path,
    output_pdf: Path | None = None,
    max_columns: int = 3,
) -> None:
    """Create full comic strip image and optional PDF."""
    if len(panel_image_paths) != len(storyboard.panels):
        raise ValueError("Panel image count must match storyboard panels")

    panel_images = [Image.open(path).convert("RGB") for path in panel_image_paths]
    panel_w, panel_h = panel_images[0].size
    caption_h = 120
    margin = 16
    columns = min(max_columns, len(panel_images))
    rows = math.ceil(len(panel_images) / columns)

    out_w = columns * panel_w + (columns + 1) * margin
    out_h = rows * (panel_h + caption_h) + (rows + 1) * margin
    strip = Image.new("RGB", (out_w, out_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(strip)
    font = ImageFont.load_default()

    for idx, panel_image in enumerate(panel_images):
        row = idx // columns
        col = idx % columns
        x = margin + col * (panel_w + margin)
        y = margin + row * (panel_h + caption_h + margin)
        strip.paste(panel_image, (x, y))
        caption_y = y + panel_h + 6
        draw.rectangle(
            (x, caption_y, x + panel_w, caption_y + caption_h - 8), outline=(0, 0, 0), width=2
        )
        panel = storyboard.panels[idx]
        caption_title = f"Panel {panel.panel_number}: {panel.teaching_intent}"
        caption_layout = layout_caption(
            panel.dialogue_or_caption, max_chars_per_line=44, max_lines=4
        )
        draw.text((x + 8, caption_y + 8), caption_title, fill=(0, 0, 0), font=font)
        draw.multiline_text(
            (x + 8, caption_y + 28),
            "\n".join(caption_layout.wrapped_lines),
            fill=(20, 20, 20),
            font=font,
            spacing=2,
        )
        draw.rectangle((x, y, x + panel_w, y + panel_h), outline=(0, 0, 0), width=3)

    output_png.parent.mkdir(parents=True, exist_ok=True)
    strip.save(output_png, format="PNG")
    if output_pdf:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        strip.save(output_pdf, format="PDF")
