from pathlib import Path

from comicstrip_tutor.reporting.quality_report import write_quality_report


def test_write_quality_report_includes_gate_and_issue_details(tmp_path: Path) -> None:
    output = tmp_path / "quality.md"
    write_quality_report(
        output_path=output,
        run_id="run-x",
        model_key="gpt-image-1-mini",
        manifest_payload={
            "completion_status": "partial_success",
            "total_estimated_cost_usd": 0.04,
            "error_type": "provider_timeout",
            "error_message": "timed out",
        },
        critique_payload={
            "overall_score": 0.72,
            "blocking_issue_count": 0,
            "major_issue_count": 1,
            "rewrite_count": 1,
            "reviewer_reports": [
                {
                    "reviewer": "technical",
                    "issues": [
                        {
                            "severity": "major",
                            "issue_code": "technical_rigor_low",
                            "message": "rigor low",
                            "recommendation": "add formalism",
                            "panel_number": 2,
                        }
                    ],
                }
            ],
            "recommended_actions": ["add formalism"],
        },
        evaluation_payload={
            "learning_effectiveness_score": 0.79,
            "comprehension_score": 0.81,
            "technical_rigor_score": 0.9,
            "publishable": False,
            "publishable_reasons": ["Technical rigor score below threshold (0.95)."],
        },
    )
    text = output.read_text(encoding="utf-8")
    assert "completion_status: `partial_success`" in text
    assert "technical_rigor_low" in text
    assert "Technical rigor score below threshold" in text
