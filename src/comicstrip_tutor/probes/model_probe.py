"""Minimal-cost model probe workflow for stability diagnostics."""

from __future__ import annotations

import re
import time

from comicstrip_tutor.config import AppConfig
from comicstrip_tutor.image_models.base import PanelImageRequest
from comicstrip_tutor.image_models.registry import create_model
from comicstrip_tutor.pipeline.error_taxonomy import classify_render_exception
from comicstrip_tutor.schemas.probe import ModelProbeResult, ProbeAttempt
from comicstrip_tutor.storage.artifact_store import ArtifactStore
from comicstrip_tutor.storage.io_utils import write_json
from comicstrip_tutor.utils.time_utils import utc_timestamp


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9.-]+", "-", value.lower()).strip("-")


def _build_probe_id(model_key: str) -> str:
    return f"probe-{_slug(model_key)}-{utc_timestamp().lower()}"


def run_model_probe(
    *,
    model_key: str,
    prompt: str,
    repetitions: int,
    width: int,
    height: int,
    dry_run: bool,
    app_config: AppConfig,
) -> ModelProbeResult:
    """Run repeated single-panel probes and persist diagnostics."""
    probe_id = _build_probe_id(model_key)
    probe_root = app_config.output_root / probe_id
    probe_root.mkdir(parents=True, exist_ok=True)
    result = ModelProbeResult(
        probe_id=probe_id,
        model_key=model_key,
        prompt=prompt,
        repetitions=repetitions,
        width=width,
        height=height,
        dry_run=dry_run,
    )
    store = ArtifactStore(app_config.output_root)

    try:
        model = create_model(model_key, app_config)
    except Exception as exc:  # noqa: BLE001
        error_type, error_message = classify_render_exception(exc)
        result.attempts.append(
            ProbeAttempt(
                attempt=1,
                success=False,
                latency_s=0.0,
                error_type=error_type,
                error_message=error_message,
            )
        )
        result.failure_count = 1
        result.success_rate = 0.0
        write_json(probe_root / "probe_result.json", result.model_dump())
        store.append_registry(
            {
                "run_id": probe_id,
                "event": "model_probe_complete",
                "model": model_key,
                "probe_success_rate": 0.0,
                "probe_failure_count": 1,
                "probe_error_type": error_type,
            }
        )
        return result

    for attempt in range(1, repetitions + 1):
        output_path = probe_root / f"attempt_{attempt:02d}.png"
        started = time.perf_counter()
        try:
            panel_result = model.generate_panel_image(
                PanelImageRequest(
                    panel_number=1,
                    prompt=prompt,
                    width=width,
                    height=height,
                    style_guide="Minimal technical illustration. Avoid embedded text.",
                    output_path=str(output_path),
                    dry_run=dry_run,
                )
            )
            elapsed = round(time.perf_counter() - started, 3)
            result.attempts.append(
                ProbeAttempt(
                    attempt=attempt,
                    success=True,
                    latency_s=elapsed,
                    provider_usage=panel_result.provider_usage,
                    image_path=panel_result.image_path,
                )
            )
            result.success_count += 1
        except Exception as exc:  # noqa: BLE001
            elapsed = round(time.perf_counter() - started, 3)
            error_type, error_message = classify_render_exception(exc)
            result.attempts.append(
                ProbeAttempt(
                    attempt=attempt,
                    success=False,
                    latency_s=elapsed,
                    error_type=error_type,
                    error_message=error_message,
                )
            )
            result.failure_count += 1

    total_attempts = len(result.attempts)
    if total_attempts > 0:
        result.success_rate = round(result.success_count / total_attempts, 4)

    output_path = probe_root / "probe_result.json"
    write_json(output_path, result.model_dump())
    store.append_registry(
        {
            "run_id": probe_id,
            "event": "model_probe_complete",
            "model": model_key,
            "probe_success_rate": result.success_rate,
            "probe_success_count": result.success_count,
            "probe_failure_count": result.failure_count,
        }
    )
    return result
