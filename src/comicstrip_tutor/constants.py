"""Project constants."""

from pathlib import Path

APP_NAME = "ComicStrip Tutor"
DEFAULT_PANEL_COUNT_DRAFT = 6
DEFAULT_PANEL_COUNT_PUBLISH = 8
DEFAULT_IMAGE_SIZE_DRAFT = (768, 768)
DEFAULT_IMAGE_SIZE_PUBLISH = (1024, 1024)

ROOT_DIR = Path.cwd()
DEFAULT_OUTPUT_ROOT = Path("runs/experiments")

CHEAP_FIRST_MODEL_ORDER = [
    "gpt-image-1-mini",
    "gemini-2.5-flash-image",
    "gpt-image-1",
    "gpt-image-1.5",
    "gemini-3-pro-image-preview",
]
