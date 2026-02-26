from pathlib import Path

from comicstrip_tutor.benchmark.runner import run_benchmark
from comicstrip_tutor.config import AppConfig


def test_mock_benchmark_flow(tmp_path: Path) -> None:
    config = AppConfig(
        openai_api_key=None,
        gemini_api_key=None,
        output_root=tmp_path / "runs",
        provider_timeout_s=30,
        provider_max_retries=1,
        provider_backoff_s=0.2,
        circuit_fail_threshold=2,
        circuit_cooldown_s=30,
        enable_experimental_models=False,
        gemini_text_image_fallback=False,
    )
    dataset = Path("benchmark/comic_benchmark_v1.json")
    result = run_benchmark(
        dataset_path=dataset,
        app_config=config,
        models=["gpt-image-1-mini", "gemini-2.5-flash-image"],
        limit=2,
        mode="draft",
        dry_run=True,
    )
    assert result.leaderboard
    benchmark_dir = config.output_root / result.benchmark_id
    assert (benchmark_dir / "leaderboard.md").exists()
    assert (benchmark_dir / "leaderboard.html").exists()
