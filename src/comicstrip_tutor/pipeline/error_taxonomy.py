"""Error classification helpers for render pipeline diagnostics."""

from __future__ import annotations

from pydantic import ValidationError

from comicstrip_tutor.image_models.reliability import CircuitOpenError, ProviderCallError


def classify_render_exception(exc: Exception) -> tuple[str, str]:
    """Classify render exceptions into stable taxonomy keys."""
    if isinstance(exc, CircuitOpenError):
        return ("provider_circuit_open", str(exc))
    if isinstance(exc, ProviderCallError):
        message = str(exc)
        if "timed out" in message.lower():
            return ("provider_timeout", message)
        return ("provider_call_failed", message)
    if isinstance(exc, TimeoutError):
        return ("provider_timeout", str(exc))
    if isinstance(exc, ValidationError):
        return ("schema_validation_failure", str(exc))
    if isinstance(exc, FileNotFoundError):
        return ("artifact_not_found", str(exc))
    if isinstance(exc, ValueError):
        return ("invalid_input", str(exc))
    return ("unknown_failure", str(exc))
