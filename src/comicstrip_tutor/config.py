"""Runtime configuration for ComicStrip Tutor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from comicstrip_tutor.constants import DEFAULT_OUTPUT_ROOT

load_dotenv()


@dataclass(slots=True, frozen=True)
class AppConfig:
    """Environment-backed app config."""

    openai_api_key: str | None
    gemini_api_key: str | None
    output_root: Path

    @classmethod
    def from_env(cls) -> AppConfig:
        output_root = Path(os.getenv("COMIC_TUTOR_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT)))
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            output_root=output_root,
        )
