"""Benchmark harness."""

from __future__ import annotations

from pathlib import Path

from pydantic import TypeAdapter

from comicstrip_tutor.benchmark.early_stop import should_early_stop
from comicstrip_tutor.benchmark.leaderboard import build_leaderboard
from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.constants import CHEAP_FIRST_MODEL_ORDER
from comicstrip_tutor.pipeline.planner_pipeline import run_planning_pipeline
from comicstrip_tutor.pipeline.render_pipeline import render_storyboard
from comicstrip_tutor.reporting.html_report import write_html_leaderboard
from comicstrip_tutor.reporting.markdown_report import write_markdown_leaderboard
from comicstrip_tutor.schemas.benchmark import (
    BenchmarkItem,
    BenchmarkModelResult,
    BenchmarkRunResult,
)
from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import read_json, write_json
from comicstrip_tutor.utils.time_utils import utc_timestamp

_BENCHMARK_ADAPTER = TypeAdapter(list[BenchmarkItem])


def _score_for_run(run_root: Path, model_key: str) -> float:
    eval_path = run_root / "evaluation" / f"{model_key}.json"
    payload = read_json(eval_path)
    metrics = payload["metrics"]
    core = [
        float(metrics["concept_coverage"]),
        float(metrics["coherence"]),
        float(metrics["visual_text_alignment"]),
        float(metrics["readability"]),
        float(metrics["consistency"]),
    ]
    if metrics.get("llm_judge") is not None:
        core.append(float(metrics["llm_judge"]))
    return round(sum(core) / len(core), 4)


def run_benchmark(
    *,
    dataset_path: Path,
    app_config: AppConfig,
    models: list[str] | None = None,
    limit: int | None = None,
    mode: str = "draft",
    dry_run: bool = True,
) -> BenchmarkRunResult:
    """Run benchmark dataset across models with early stopping."""
    benchmark_id = f"benchmark-{utc_timestamp()}"
    dataset = _BENCHMARK_ADAPTER.validate_python(read_json(dataset_path))
    if limit:
        dataset = dataset[:limit]
    model_order = models or CHEAP_FIRST_MODEL_ORDER
    store = ArtifactStore(app_config.output_root)
    results: list[BenchmarkModelResult] = []
    best_mean_so_far = 0.0

    for model_key in model_order:
        model_scores: list[float] = []
        for item in dataset:
            run_id = f"{benchmark_id}-{item.id}-{model_key}".replace(" ", "-").lower()
            run_config = RunConfig(
                run_id=run_id,
                topic=item.topic,
                audience_level=item.audience_level,
                panel_count=6 if mode == "draft" else 8,
                mode=mode,  # type: ignore[arg-type]
            )
            run_planning_pipeline(run_config=run_config, artifact_store=store)
            manifest = render_storyboard(
                run_id=run_id,
                model_key=model_key,
                mode=mode,
                dry_run=dry_run,
                app_config=app_config,
                expected_key_points=item.expected_key_points,
                enable_llm_judge=False,
            )
            score = _score_for_run(store.open_run(run_id).root, model_key)
            model_scores.append(score)
            results.append(
                BenchmarkModelResult(
                    item_id=item.id,
                    model_key=model_key,
                    score=score,
                    cost_usd=manifest.total_estimated_cost_usd,
                    run_id=run_id,
                )
            )
            if should_early_stop(model_scores=model_scores, best_mean_so_far=best_mean_so_far):
                break
        if model_scores:
            mean_score = sum(model_scores) / len(model_scores)
            best_mean_so_far = max(best_mean_so_far, mean_score)

    leaderboard = build_leaderboard(results)
    run_result = BenchmarkRunResult(
        benchmark_id=benchmark_id,
        model_results=results,
        leaderboard=leaderboard,
    )
    benchmark_dir = app_config.output_root / benchmark_id
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    write_json(benchmark_dir / "benchmark_result.json", run_result.model_dump())
    write_markdown_leaderboard(
        output_path=benchmark_dir / "leaderboard.md",
        benchmark_id=benchmark_id,
        leaderboard=leaderboard,
    )
    write_html_leaderboard(
        output_path=benchmark_dir / "leaderboard.html",
        benchmark_id=benchmark_id,
        leaderboard=leaderboard,
    )
    store.append_registry(
        {"run_id": benchmark_id, "event": "benchmark_complete", "models": model_order}
    )
    return run_result
