"""Pipeline helpers for critique execution and persistence."""

from __future__ import annotations

from pathlib import Path

from comicstrip_tutor.critique.orchestrator import run_storyboard_critique
from comicstrip_tutor.schemas.critique import CritiqueReport
from comicstrip_tutor.schemas.runs import CritiqueMode
from comicstrip_tutor.schemas.storyboard import Storyboard
from comicstrip_tutor.storage.io_utils import write_json


def run_and_save_critique(
    *,
    run_id: str,
    stage: str,
    critique_mode: CritiqueMode,
    storyboard: Storyboard,
    expected_key_points: list[str],
    misconceptions: list[str],
    audience_level: str,
    output_path: Path,
) -> CritiqueReport:
    """Run critique and persist report as JSON."""
    report = run_storyboard_critique(
        run_id=run_id,
        stage=stage,
        critique_mode=critique_mode,
        storyboard=storyboard,
        expected_key_points=expected_key_points,
        misconceptions=misconceptions,
        audience_level=audience_level,
    )
    write_json(output_path, report.model_dump())
    return report
