"""Planning and storyboard pipeline."""

from __future__ import annotations

from comicstrip_tutor.llm.text_planner import PlanningBundle, build_plan
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import write_json
from comicstrip_tutor.utils.hashing import sha256_text


def run_planning_pipeline(
    *,
    run_config: RunConfig,
    artifact_store: ArtifactStore,
) -> tuple[PlanningBundle, str]:
    """Generate planning artifacts and storyboard."""
    paths = artifact_store.create_run(run_config)
    bundle = build_plan(
        topic=run_config.topic,
        source_text=run_config.source_text,
        panel_count=run_config.panel_count,
        audience_level=run_config.audience_level,
    )
    write_json(paths.planning_dir / "learning_plan.json", bundle.learning_plan.model_dump())
    write_json(paths.planning_dir / "story_arc.json", bundle.story_arc.model_dump())
    write_json(
        paths.planning_dir / "characters.json",
        [character.model_dump() for character in bundle.characters],
    )
    write_json(paths.root / "storyboard.json", bundle.storyboard.model_dump())
    storyboard_hash = sha256_text(bundle.storyboard.model_dump_json())
    write_json(paths.root / "storyboard_meta.json", {"storyboard_hash": storyboard_hash})
    artifact_store.append_registry(
        {
            "run_id": run_config.run_id,
            "event": "planning_complete",
            "storyboard_hash": storyboard_hash,
        }
    )
    return bundle, storyboard_hash
