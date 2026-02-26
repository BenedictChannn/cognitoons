"""Planning and storyboard pipeline."""

from __future__ import annotations

from dataclasses import asdict

from comicstrip_tutor.critique.orchestrator import should_block_render
from comicstrip_tutor.llm.text_planner import PlanningBundle, build_plan
from comicstrip_tutor.pipeline.critique_pipeline import run_critique_with_rewrites
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import write_json
from comicstrip_tutor.styles.compiler import compile_style_guide
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
        template=run_config.template,
        theme=run_config.theme,
    )
    write_json(paths.planning_dir / "learning_plan.json", bundle.learning_plan.model_dump())
    write_json(paths.planning_dir / "story_arc.json", bundle.story_arc.model_dump())
    write_json(
        paths.planning_dir / "characters.json",
        [character.model_dump() for character in bundle.characters],
    )
    compiled_style = compile_style_guide(
        template_id=run_config.template,
        theme_id=run_config.theme,
        audience_level=run_config.audience_level,
    )
    write_json(
        paths.planning_dir / "style_guide.json",
        {
            "template": asdict(compiled_style.template),
            "theme": asdict(compiled_style.theme),
            "style_text": compiled_style.style_text,
            "visual_instruction": compiled_style.visual_instruction,
            "pedagogy_instruction": compiled_style.pedagogy_instruction,
        },
    )
    critique_max_iterations = run_config.critique_max_iterations
    if critique_max_iterations is None:
        critique_max_iterations = 4 if run_config.mode == "publish" else 2
    rewritten_storyboard, critique_report, rewrite_count = run_critique_with_rewrites(
        run_id=run_config.run_id,
        stage="post_planning",
        critique_mode=run_config.critique_mode,
        storyboard=bundle.storyboard,
        expected_key_points=bundle.learning_plan.objectives,
        misconceptions=bundle.learning_plan.misconceptions,
        audience_level=run_config.audience_level,
        output_dir=paths.critiques_dir,
        max_iterations=critique_max_iterations,
        auto_rewrite=run_config.auto_rewrite,
    )
    bundle.storyboard = rewritten_storyboard
    write_json(paths.root / "storyboard.json", rewritten_storyboard.model_dump())
    if should_block_render(critique_report):
        raise RuntimeError(
            "Planning blocked by critique gate after rewrite loop: "
            f"{critique_report.blocking_issue_count} critical and "
            f"{critique_report.major_issue_count} major issues."
        )
    storyboard_hash = sha256_text(rewritten_storyboard.model_dump_json())
    write_json(paths.root / "storyboard_meta.json", {"storyboard_hash": storyboard_hash})
    artifact_store.append_registry(
        {
            "run_id": run_config.run_id,
            "event": "planning_complete",
            "storyboard_hash": storyboard_hash,
            "critique_score": critique_report.overall_score,
            "critique_rewrites": rewrite_count,
        }
    )
    return bundle, storyboard_hash
