from comicstrip_tutor.schemas.runs import PanelRenderRecord


def test_panel_render_record_accepts_nested_provider_usage() -> None:
    record = PanelRenderRecord(
        panel_number=1,
        prompt_path="panel_01.txt",
        image_path="panel_01.png",
        estimated_cost_usd=0.01,
        provider_usage={
            "total_tokens": 120,
            "input_tokens_details": {"text_tokens": 100, "image_tokens": 20},
            "output_tokens_details": None,
        },
    )
    assert isinstance(record.provider_usage["input_tokens_details"], dict)
