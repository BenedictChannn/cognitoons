"""Storyboard editing helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import TypeAdapter

from comicstrip_tutor.schemas.storyboard import Storyboard
from comicstrip_tutor.storage.io_utils import read_json, write_json

_STORYBOARD_ADAPTER = TypeAdapter(Storyboard)


def load_storyboard(path: Path) -> Storyboard:
    """Load and validate storyboard JSON."""
    return _STORYBOARD_ADAPTER.validate_python(read_json(path))


def save_storyboard(path: Path, storyboard: Storyboard) -> None:
    """Save storyboard."""
    write_json(path, storyboard.model_dump())


def open_in_editor(path: Path, editor: str) -> None:
    """Open file in terminal editor and wait for close."""
    subprocess.run([editor, str(path)], check=True)


def validate_storyboard_file(path: Path) -> Storyboard:
    """Validate edited storyboard file and return parsed model."""
    return load_storyboard(path)
