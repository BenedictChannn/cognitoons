"""Artifact directory management and experiment registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from comicstrip_tutor.constants import DEFAULT_OUTPUT_ROOT
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.io_utils import write_json, write_text
from comicstrip_tutor.utils.time_utils import utc_timestamp


@dataclass(slots=True)
class RunPaths:
    """Structured paths for a run."""

    run_id: str
    root: Path
    planning_dir: Path
    prompts_dir: Path
    images_dir: Path
    composite_dir: Path
    evaluations_dir: Path
    reports_dir: Path


class ArtifactStore:
    """Handles run directory setup and metadata writes."""

    def __init__(self, output_root: Path | None = None):
        self.output_root = output_root or DEFAULT_OUTPUT_ROOT
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.output_root.parent / "experiment_registry.jsonl"

    def create_run(self, config: RunConfig) -> RunPaths:
        run_id = config.run_id or f"run-{utc_timestamp()}"
        root = self.output_root / run_id
        planning = root / "planning"
        prompts = root / "panel_prompts"
        images = root / "images"
        composite = root / "composite"
        evaluations = root / "evaluation"
        reports = root / "reports"
        for path in [root, planning, prompts, images, composite, evaluations, reports]:
            path.mkdir(parents=True, exist_ok=True)
        write_json(root / "run_config.json", config.model_dump())
        return RunPaths(
            run_id=run_id,
            root=root,
            planning_dir=planning,
            prompts_dir=prompts,
            images_dir=images,
            composite_dir=composite,
            evaluations_dir=evaluations,
            reports_dir=reports,
        )

    def open_run(self, run_id: str) -> RunPaths:
        root = self.output_root / run_id
        if not root.exists():
            raise FileNotFoundError(f"Run not found: {run_id}")
        return RunPaths(
            run_id=run_id,
            root=root,
            planning_dir=root / "planning",
            prompts_dir=root / "panel_prompts",
            images_dir=root / "images",
            composite_dir=root / "composite",
            evaluations_dir=root / "evaluation",
            reports_dir=root / "reports",
        )

    def append_registry(self, line: dict) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"timestamp": utc_timestamp(), **line}, ensure_ascii=False) + "\n"
        if self.registry_path.exists():
            existing = self.registry_path.read_text(encoding="utf-8")
            write_text(self.registry_path, existing + payload)
            return
        write_text(self.registry_path, payload)
