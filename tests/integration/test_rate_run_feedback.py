import json
from pathlib import Path

from typer.testing import CliRunner

from comicstrip_tutor.cli import app

runner = CliRunner()


def test_rate_run_records_feedback_and_updates_bandit(tmp_path: Path, monkeypatch) -> None:
    output_root = tmp_path / "experiments"
    run_id = "rate-run-demo"
    run_root = output_root / run_id
    evaluation_dir = run_root / "evaluation"
    reports_dir = run_root / "reports"
    for path in [run_root, evaluation_dir, reports_dir]:
        path.mkdir(parents=True, exist_ok=True)

    (run_root / "run_config.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "topic": "topic",
                "panel_count": 4,
                "mode": "draft",
                "template": "misconception-first",
                "theme": "textbook-modern",
                "image_text_mode": "none",
            }
        ),
        encoding="utf-8",
    )
    (run_root / "manifest_gpt-image-1-mini.json").write_text(
        json.dumps({"total_estimated_cost_usd": 0.08}),
        encoding="utf-8",
    )
    (evaluation_dir / "gpt-image-1-mini.json").write_text(
        json.dumps({"learning_effectiveness_score": 0.9}),
        encoding="utf-8",
    )
    monkeypatch.setenv("COMIC_TUTOR_OUTPUT_ROOT", str(output_root))

    result = runner.invoke(
        app,
        [
            "rate-run",
            run_id,
            "--model",
            "gpt-image-1-mini",
            "--rating",
            "4",
            "--note",
            "Great flow",
        ],
    )
    assert result.exit_code == 0

    feedback_path = reports_dir / "user_feedback_gpt-image-1-mini.json"
    assert feedback_path.exists()
    bandit_path = output_root.parent / "exploration_bandit.json"
    payload = json.loads(bandit_path.read_text(encoding="utf-8"))
    arms = payload["arms"]
    arm_key = "misconception-first|textbook-modern|gpt-image-1-mini|none"
    assert arm_key in arms
    assert int(arms[arm_key]["pulls"]) >= 1
