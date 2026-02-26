from comicstrip_tutor.benchmark.leaderboard import build_leaderboard
from comicstrip_tutor.schemas.benchmark import BenchmarkModelResult


def test_leaderboard_aggregates_les_and_publish_gate_rate() -> None:
    rows = [
        BenchmarkModelResult(
            item_id="a",
            model_key="gpt-image-1-mini",
            score=0.7,
            learning_effectiveness_score=0.82,
            comprehension_score=0.84,
            technical_rigor_score=0.96,
            publishable=True,
            cost_usd=0.01,
            run_id="run-a",
        ),
        BenchmarkModelResult(
            item_id="b",
            model_key="gpt-image-1-mini",
            score=0.6,
            learning_effectiveness_score=0.78,
            comprehension_score=0.79,
            technical_rigor_score=0.94,
            publishable=False,
            publishable_reasons=["Technical rigor score below threshold (0.95)."],
            cost_usd=0.02,
            run_id="run-b",
        ),
    ]
    leaderboard = build_leaderboard(rows)
    assert len(leaderboard) == 1
    row = leaderboard[0]
    assert row["model_key"] == "gpt-image-1-mini"
    assert float(row["mean_les"]) == 0.8
    assert float(row["publish_gate_pass_rate"]) == 0.5
    assert "Technical rigor score below threshold" in str(row["top_gate_failures"])
