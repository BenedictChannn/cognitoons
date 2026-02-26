from pathlib import Path

from comicstrip_tutor.reporting.trend_report import write_trend_report


def test_write_trend_report_aggregates_registry_events(tmp_path: Path) -> None:
    registry = tmp_path / "experiment_registry.jsonl"
    registry.write_text(
        "\n".join(
            [
                '{"event":"render_complete","model":"gpt-image-1-mini","aggregate_score":0.9,"estimated_cost_usd":0.02}',
                '{"event":"render_complete","model":"gpt-image-1-mini","aggregate_score":0.8,"estimated_cost_usd":0.01}',
                '{"event":"render_failed","model":"gemini-3-pro-image-preview","error_type":"provider_timeout"}',
                '{"event":"user_feedback","model":"gpt-image-1-mini","rating":5}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "trend.md"
    write_trend_report(registry_path=registry, output_path=output)
    text = output.read_text(encoding="utf-8")
    assert "render_complete: `2`" in text
    assert "| gpt-image-1-mini | 0.8500 | 0.0150 | 2 |" in text
    assert "| provider_timeout | 1 |" in text
    assert "| gpt-image-1-mini | 5.00 | 1 |" in text
