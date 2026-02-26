from pydantic import BaseModel, TypeAdapter, ValidationError

from comicstrip_tutor.pipeline.error_taxonomy import classify_render_exception


def test_classify_timeout_error() -> None:
    error_type, _ = classify_render_exception(TimeoutError("timed out"))
    assert error_type == "provider_timeout"


def test_classify_validation_error() -> None:
    class _Model(BaseModel):
        value: int

    adapter = TypeAdapter(_Model)
    try:
        adapter.validate_python({})
    except ValidationError as exc:
        error_type, _ = classify_render_exception(exc)
    assert error_type == "schema_validation_failure"


def test_classify_experimental_model_disabled_error() -> None:
    error_type, _ = classify_render_exception(
        ValueError("Model 'gemini-3.1-flash-image-preview' is experimental.")
    )
    assert error_type == "experimental_model_disabled"
