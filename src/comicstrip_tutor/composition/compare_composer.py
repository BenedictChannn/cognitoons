"""Side-by-side model comparison composer."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def compose_comparison(
    *,
    panel_paths_a: list[str],
    panel_paths_b: list[str],
    model_a: str,
    model_b: str,
    output_path: Path,
) -> None:
    """Create side-by-side panel comparison image."""
    if len(panel_paths_a) != len(panel_paths_b):
        raise ValueError("Comparison requires equal panel counts")
    panels_a = [Image.open(path).convert("RGB") for path in panel_paths_a]
    panels_b = [Image.open(path).convert("RGB") for path in panel_paths_b]
    panel_w, panel_h = panels_a[0].size
    margin = 16
    header_h = 44
    rows = len(panels_a)
    canvas_w = margin * 3 + panel_w * 2
    canvas_h = margin * (rows + 1) + rows * panel_h + header_h
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((margin, 8), f"A: {model_a}", fill=(0, 0, 0), font=font)
    draw.text((margin * 2 + panel_w, 8), f"B: {model_b}", fill=(0, 0, 0), font=font)
    for idx in range(rows):
        y = header_h + margin + idx * (panel_h + margin)
        left_x = margin
        right_x = margin * 2 + panel_w
        canvas.paste(panels_a[idx], (left_x, y))
        canvas.paste(panels_b[idx], (right_x, y))
        draw.rectangle((left_x, y, left_x + panel_w, y + panel_h), outline=(0, 0, 0), width=2)
        draw.rectangle((right_x, y, right_x + panel_w, y + panel_h), outline=(0, 0, 0), width=2)
        draw.text((4, y + 4), f"P{idx + 1}", fill=(0, 0, 0), font=font)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG")
