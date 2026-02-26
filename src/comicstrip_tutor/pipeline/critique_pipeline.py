"""Pipeline helpers for critique execution and persistence."""

from __future__ import annotations

from pathlib import Path

from comicstrip_tutor.critique.orchestrator import needs_rewrite, run_storyboard_critique
from comicstrip_tutor.critique.rewrite import apply_targeted_rewrites
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


def run_critique_with_rewrites(
    *,
    run_id: str,
    stage: str,
    critique_mode: CritiqueMode,
    storyboard: Storyboard,
    expected_key_points: list[str],
    misconceptions: list[str],
    audience_level: str,
    output_dir: Path,
    max_iterations: int,
    auto_rewrite: bool,
) -> tuple[Storyboard, CritiqueReport, int]:
    """Run critique loop with optional targeted storyboard rewrites."""
    current_storyboard = storyboard.model_copy(deep=True)
    rewrite_count = 0
    final_report: CritiqueReport | None = None
    final_report_path = output_dir / f"{stage}.json"

    for iteration in range(max_iterations + 1):
        report = run_storyboard_critique(
            run_id=run_id,
            stage=stage,
            critique_mode=critique_mode,
            storyboard=current_storyboard,
            expected_key_points=expected_key_points,
            misconceptions=misconceptions,
            audience_level=audience_level,
        )
        iteration_report = {
            **report.model_dump(),
            "iteration": iteration,
            "auto_rewrite_enabled": auto_rewrite,
        }
        write_json(output_dir / f"{stage}_iter_{iteration:02d}.json", iteration_report)
        final_report = report
        if critique_mode == "off":
            break
        if not needs_rewrite(report):
            break
        if not auto_rewrite or iteration >= max_iterations:
            break
        rewritten_storyboard, rewrite_notes = apply_targeted_rewrites(
            storyboard=current_storyboard,
            critique_report=report,
            expected_key_points=expected_key_points,
            misconceptions=misconceptions,
        )
        if not rewrite_notes:
            break
        current_storyboard = rewritten_storyboard
        rewrite_count += 1
        write_json(
            output_dir / f"{stage}_rewrite_{iteration:02d}.json",
            {"iteration": iteration, "rewrite_notes": rewrite_notes},
        )

    if final_report is None:
        raise RuntimeError("Critique loop failed to produce report.")
    write_json(final_report_path, {**final_report.model_dump(), "rewrite_count": rewrite_count})
    return current_storyboard, final_report, rewrite_count
