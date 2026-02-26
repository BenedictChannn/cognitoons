"""ComicStrip Tutor CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from comicstrip_tutor.benchmark.runner import run_benchmark
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.exploration.arms import build_arm_id
from comicstrip_tutor.exploration.bandit import ExplorationBanditStore
from comicstrip_tutor.image_models.registry import list_models
from comicstrip_tutor.logging_utils import configure_logging
from comicstrip_tutor.pipeline.compare_pipeline import compare_models_on_storyboard
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.pipeline.render_pipeline import render_storyboard
from comicstrip_tutor.pipeline.reroll_pipeline import reroll_single_panel
from comicstrip_tutor.pipeline.storyboard_editor import (
    load_storyboard,
    open_in_editor,
    save_storyboard,
    validate_storyboard_file,
)
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.build_log import BuildLogEntry, append_build_log, ensure_topic_log
from comicstrip_tutor.storage.io_utils import read_json, write_json
from comicstrip_tutor.styles.templates import list_templates
from comicstrip_tutor.styles.themes import list_themes
from comicstrip_tutor.utils.time_utils import utc_timestamp

app = typer.Typer(help="ComicStrip Tutor: storyboard-first technical comics")
console = Console()


def _app_config() -> AppConfig:
    return AppConfig.from_env()


def _new_run_id() -> str:
    return f"comic-{utc_timestamp().lower()}"


def _bandit_store() -> ExplorationBanditStore:
    return ExplorationBanditStore(_app_config().output_root.parent / "exploration_bandit.json")


@app.callback()
def common(verbose: bool = typer.Option(False, "--verbose", help="Verbose logging")) -> None:
    """Global options."""
    configure_logging(verbose=verbose)


@app.command("list-models")
def list_models_command() -> None:
    """List supported image models."""
    table = Table(title="Supported Image Models")
    table.add_column("Model")
    for model in list_models():
        table.add_row(model)
    console.print(table)


@app.command("list-templates")
def list_templates_command() -> None:
    """List pedagogy templates."""
    table = Table(title="Pedagogy Templates")
    table.add_column("Template ID")
    table.add_column("Title")
    table.add_column("Description")
    for template in list_templates():
        table.add_row(template.template_id, template.title, template.description)
    console.print(table)


@app.command("list-themes")
def list_themes_command() -> None:
    """List visual theme packs."""
    table = Table(title="Theme Packs")
    table.add_column("Theme ID")
    table.add_column("Title")
    table.add_column("Description")
    for theme in list_themes():
        table.add_row(theme.theme_id, theme.title, theme.description)
    console.print(table)


@app.command("suggest-arm")
def suggest_arm(
    models: str = typer.Option("gpt-image-1-mini,gemini-2.5-flash-image", "--models"),
    templates: str = typer.Option("intuition-to-formalism,misconception-first", "--templates"),
    themes: str = typer.Option("clean-whiteboard,textbook-modern", "--themes"),
    text_modes: str = typer.Option("none,minimal", "--text-modes"),
    exploration_c: float = typer.Option(1.2, "--exploration-c"),
) -> None:
    """Suggest next exploration arm using UCB scoring."""
    model_list = [entry.strip() for entry in models.split(",") if entry.strip()]
    template_list = [entry.strip() for entry in templates.split(",") if entry.strip()]
    theme_list = [entry.strip() for entry in themes.split(",") if entry.strip()]
    text_mode_list = [entry.strip() for entry in text_modes.split(",") if entry.strip()]
    candidates = [
        build_arm_id(
            template=template,
            theme=theme,
            model_key=model,
            image_text_mode=text_mode,
        )
        for template in template_list
        for theme in theme_list
        for model in model_list
        for text_mode in text_mode_list
    ]
    suggested = _bandit_store().suggest_arm(candidate_arms=candidates, exploration_c=exploration_c)
    console.print(f"[green]Suggested arm:[/green] {suggested}")


@app.command("bandit-stats")
def bandit_stats(limit: int = typer.Option(10, "--limit", min=1)) -> None:
    """Show top exploration arm stats."""
    stats = _bandit_store().all_stats()
    stats_sorted = sorted(stats, key=lambda item: item.mean_reward, reverse=True)[:limit]
    table = Table(title="Exploration Bandit Stats")
    table.add_column("Arm")
    table.add_column("Pulls")
    table.add_column("Mean Reward")
    table.add_column("Total Cost")
    for stat in stats_sorted:
        table.add_row(
            stat.arm_id,
            str(stat.pulls),
            f"{stat.mean_reward:.4f}",
            f"{stat.total_cost_usd:.4f}",
        )
    console.print(table)


@app.command("rate-run")
def rate_run(
    run_id: str = typer.Argument(...),
    model: str = typer.Option(..., "--model"),
    rating: int = typer.Option(..., "--rating", min=1, max=5),
    note: str | None = typer.Option(None, "--note"),
) -> None:
    """Record user preference rating for a rendered run."""
    config = _app_config()
    store = ArtifactStore(config.output_root)
    paths = store.open_run(run_id)
    run_config_payload = read_json(paths.root / "run_config.json")
    manifest_payload = read_json(paths.root / f"manifest_{model}.json")
    evaluation_payload = read_json(paths.evaluations_dir / f"{model}.json")

    template = str(run_config_payload.get("template", "intuition-to-formalism"))
    theme = str(run_config_payload.get("theme", "clean-whiteboard"))
    image_text_mode = str(run_config_payload.get("image_text_mode", "none"))
    arm_id = build_arm_id(
        template=template,
        theme=theme,
        model_key=model,
        image_text_mode=image_text_mode,
    )
    rating_reward = rating / 5.0
    les_score = evaluation_payload.get("learning_effectiveness_score")
    les_reward = float(les_score) if les_score is not None else rating_reward
    blended_reward = round((0.7 * les_reward) + (0.3 * rating_reward), 4)
    total_cost_usd = float(manifest_payload.get("total_estimated_cost_usd", 0.0))

    _bandit_store().record(
        arm_id=arm_id,
        reward=blended_reward,
        cost_usd=total_cost_usd,
    )
    feedback_payload = {
        "run_id": run_id,
        "model_key": model,
        "arm_id": arm_id,
        "user_rating": rating,
        "rating_reward": rating_reward,
        "les_reward": les_reward,
        "blended_reward": blended_reward,
        "note": note or "",
    }
    feedback_path = paths.reports_dir / f"user_feedback_{model}.json"
    write_json(feedback_path, feedback_payload)
    store.append_registry(
        {
            "run_id": run_id,
            "event": "user_feedback",
            "model": model,
            "arm_id": arm_id,
            "rating": rating,
            "blended_reward": blended_reward,
        }
    )
    console.print(f"[green]Recorded feedback for[/green] {run_id} / {model}")
    console.print(f"[green]Arm:[/green] {arm_id}")
    console.print(f"[green]Blended reward:[/green] {blended_reward:.4f}")


@app.command("generate")
def generate(
    topic: str | None = typer.Option(None, "--topic"),
    source_text: str | None = typer.Option(None, "--source-text"),
    source_file: Path | None = typer.Option(None, "--source-file"),
    audience_level: str = typer.Option("beginner", "--audience-level"),
    panel_count: int = typer.Option(6, "--panel-count", min=4, max=12),
    mode: str = typer.Option("draft", "--mode"),
    critique_mode: str = typer.Option("warn", "--critique-mode"),
    critique_max_iterations: int | None = typer.Option(None, "--critique-max-iterations"),
    auto_rewrite: bool = typer.Option(True, "--auto-rewrite/--no-auto-rewrite"),
    image_text_mode: str = typer.Option("none", "--image-text-mode"),
    template: str = typer.Option("intuition-to-formalism", "--template"),
    theme: str = typer.Option("clean-whiteboard", "--theme"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Generate planning artifacts + storyboard."""
    if source_file:
        source_text = source_file.read_text(encoding="utf-8")
    if not topic and not source_text:
        raise typer.BadParameter("Provide --topic or --source-text/--source-file")
    rid = run_id or _new_run_id()
    config = RunConfig(
        run_id=rid,
        topic=topic,
        source_text=source_text,
        audience_level=audience_level,
        panel_count=panel_count,
        mode=mode,  # type: ignore[arg-type]
        critique_mode=critique_mode,  # type: ignore[arg-type]
        critique_max_iterations=critique_max_iterations,
        auto_rewrite=auto_rewrite,
        image_text_mode=image_text_mode,  # type: ignore[arg-type]
        template=template,
        theme=theme,
    )
    store = ArtifactStore(_app_config().output_root)
    bundle, storyboard_hash = run_planning_pipeline(run_config=config, artifact_store=store)
    console.print(f"[green]Created run:[/green] {rid}")
    console.print(f"[green]Storyboard hash:[/green] {storyboard_hash[:12]}...")
    console.print(f"[green]Panels:[/green] {len(bundle.storyboard.panels)}")


@app.command("edit-storyboard")
def edit_storyboard(
    run_id: str = typer.Argument(...),
    open_editor_flag: bool = typer.Option(False, "--open-editor"),
    editor: str = typer.Option("", "--editor"),
) -> None:
    """Validate/edit storyboard before rendering."""
    store = ArtifactStore(_app_config().output_root)
    paths = store.open_run(run_id)
    storyboard_path = paths.root / "storyboard.json"
    storyboard = load_storyboard(storyboard_path)
    if open_editor_flag:
        chosen_editor = editor or os.getenv("EDITOR", "vi")
        open_in_editor(storyboard_path, chosen_editor)
        storyboard = validate_storyboard_file(storyboard_path)
        save_storyboard(storyboard_path, storyboard)
    console.print(
        f"[green]Storyboard valid for run[/green] {run_id}: {len(storyboard.panels)} panels"
    )


@app.command("render")
def render(
    run_id: str = typer.Argument(...),
    model: str = typer.Option(..., "--model"),
    mode: str = typer.Option("draft", "--mode"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    llm_judge: bool = typer.Option(False, "--llm-judge"),
    critique_mode: str | None = typer.Option(None, "--critique-mode"),
    image_text_mode: str | None = typer.Option(None, "--image-text-mode"),
    auto_rewrite: bool | None = typer.Option(None, "--auto-rewrite/--no-auto-rewrite"),
    critique_max_iterations: int | None = typer.Option(None, "--critique-max-iterations"),
    allow_fallback: bool = typer.Option(True, "--allow-fallback/--no-fallback"),
) -> None:
    """Render comic strip with selected model."""
    manifest = render_storyboard(
        run_id=run_id,
        model_key=model,
        mode=mode,
        dry_run=dry_run,
        app_config=_app_config(),
        enable_llm_judge=llm_judge,
        critique_mode=critique_mode,  # type: ignore[arg-type]
        image_text_mode=image_text_mode,  # type: ignore[arg-type]
        allow_model_fallback=allow_fallback,
        auto_rewrite=auto_rewrite,
        critique_max_iterations=critique_max_iterations,
    )
    console.print(f"[green]Rendered[/green] {run_id} with {model}")
    console.print(f"[green]Estimated cost:[/green] ${manifest.total_estimated_cost_usd:.4f}")


@app.command("reroll-panel")
def reroll_panel(
    run_id: str = typer.Argument(...),
    model: str = typer.Option(..., "--model"),
    panel: int = typer.Option(..., "--panel", min=1),
    metaphor: str | None = typer.Option(None, "--metaphor"),
    mode: str = typer.Option("draft", "--mode"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Regenerate one panel only."""
    output = reroll_single_panel(
        run_id=run_id,
        model_key=model,
        panel_number=panel,
        metaphor=metaphor,
        mode=mode,
        dry_run=dry_run,
        app_config=_app_config(),
    )
    console.print(f"[green]Rerolled panel[/green] {panel}: {output}")


@app.command("compare")
def compare(
    run_id: str = typer.Argument(...),
    model_a: str = typer.Option(..., "--model-a"),
    model_b: str = typer.Option(..., "--model-b"),
    mode: str = typer.Option("draft", "--mode"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Compare two models on same storyboard."""
    summary = compare_models_on_storyboard(
        run_id=run_id,
        model_a=model_a,
        model_b=model_b,
        mode=mode,
        dry_run=dry_run,
        app_config=_app_config(),
    )
    console.print(f"[green]Comparison image:[/green] {summary.output_path}")


@app.command("benchmark")
def benchmark(
    dataset: Path = typer.Option(Path("benchmark/comic_benchmark_v1.json"), "--dataset"),
    limit: int = typer.Option(10, "--limit", min=1),
    mode: str = typer.Option("draft", "--mode"),
    dry_run: bool = typer.Option(True, "--dry-run"),
    models: str = typer.Option("cheap-first", "--models"),
) -> None:
    """Run benchmark sweep and leaderboard report generation."""
    selected_models = None
    if models != "cheap-first":
        selected_models = [entry.strip() for entry in models.split(",") if entry.strip()]
    result = run_benchmark(
        dataset_path=dataset,
        app_config=_app_config(),
        models=selected_models,
        limit=limit,
        mode=mode,
        dry_run=dry_run,
    )
    table = Table(title=f"Benchmark {result.benchmark_id}")
    table.add_column("Model")
    table.add_column("Mean LES")
    table.add_column("Mean Score")
    table.add_column("Publish Gate Pass")
    table.add_column("Top Gate Failure")
    table.add_column("Total Cost (USD)")
    for row in result.leaderboard:
        mean_les = float(row.get("mean_les", row["mean_score"]))
        publish_gate = float(row.get("publish_gate_pass_rate", 0.0))
        top_gate_failures = str(row.get("top_gate_failures", "none"))
        first_failure = top_gate_failures.split(";")[0].strip()
        table.add_row(
            str(row["model_key"]),
            f"{mean_les:.4f}",
            f"{row['mean_score']:.4f}",
            f"{publish_gate:.4f}",
            first_failure,
            f"{row['total_cost_usd']:.4f}",
        )
    console.print(table)
    console.print(
        f"[green]Reports written under[/green] {_app_config().output_root / result.benchmark_id}"
    )


@app.command("report")
def report(benchmark_run: str = typer.Option(..., "--benchmark-run")) -> None:
    """Print benchmark report paths and summary."""
    benchmark_dir = _app_config().output_root / benchmark_run
    result_path = benchmark_dir / "benchmark_result.json"
    if not result_path.exists():
        raise typer.BadParameter(f"Benchmark result not found: {result_path}")
    payload = read_json(result_path)
    console.print(f"[green]Markdown:[/green] {benchmark_dir / 'leaderboard.md'}")
    console.print(f"[green]HTML:[/green] {benchmark_dir / 'leaderboard.html'}")
    console.print(json.dumps(payload.get("leaderboard", []), indent=2))


@app.command("build-log")
def build_log(
    intent: str = typer.Option(..., "--intent"),
    topic: str = typer.Option(..., "--topic"),
    title: str = typer.Option(..., "--title"),
    summary: list[str] = typer.Option([], "--summary"),
    details: list[str] = typer.Option([], "--details"),
    files_touched: list[str] = typer.Option([], "--file"),
    impact: list[str] = typer.Option([], "--impact"),
    follow_ups: list[str] = typer.Option([], "--follow-up"),
    references: list[str] = typer.Option([], "--ref"),
) -> None:
    """Create/update topic build log entry."""
    if intent not in {"create", "update"}:
        raise typer.BadParameter("--intent must be create|update")
    if intent == "create":
        path = ensure_topic_log(topic)
        console.print(f"[green]Created topic log:[/green] {path}")
        return
    path = append_build_log(
        topic,
        BuildLogEntry(
            title=title,
            summary=summary,
            details=details,
            files_touched=files_touched,
            impact=impact,
            follow_ups=follow_ups,
            references=references,
        ),
    )
    console.print(f"[green]Updated build log:[/green] {path}")


if __name__ == "__main__":
    app()
