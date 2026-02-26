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
    provider_timeout_s: float
    provider_max_retries: int
    provider_backoff_s: float
    circuit_fail_threshold: int
    circuit_cooldown_s: float

    @classmethod
    def from_env(cls) -> AppConfig:
        output_root = Path(os.getenv("COMIC_TUTOR_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT)))
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            output_root=output_root,
            provider_timeout_s=float(os.getenv("COMIC_TUTOR_PROVIDER_TIMEOUT_S", "90")),
            provider_max_retries=int(os.getenv("COMIC_TUTOR_PROVIDER_MAX_RETRIES", "2")),
            provider_backoff_s=float(os.getenv("COMIC_TUTOR_PROVIDER_BACKOFF_S", "1.5")),
            circuit_fail_threshold=int(os.getenv("COMIC_TUTOR_CIRCUIT_FAIL_THRESHOLD", "3")),
            circuit_cooldown_s=float(os.getenv("COMIC_TUTOR_CIRCUIT_COOLDOWN_S", "300")),
        )
