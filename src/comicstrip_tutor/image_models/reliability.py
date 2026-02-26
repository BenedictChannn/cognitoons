"""Reliability helpers: timeout, retry, and circuit breaker."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import Thread

from comicstrip_tutor.storage.cache import JsonCache


@dataclass(slots=True, frozen=True)
class ReliabilityPolicy:
    """Policy controlling provider call resilience."""

    timeout_s: float
    max_retries: int
    backoff_s: float
    circuit_fail_threshold: int
    circuit_cooldown_s: float


class ProviderCallError(RuntimeError):
    """Raised when provider call fails after retries."""


class CircuitOpenError(RuntimeError):
    """Raised when circuit breaker is open for provider/model."""


class CircuitBreakerStore:
    """Persistent circuit breaker state store."""

    def __init__(self, path: Path):
        self._cache = JsonCache(path)

    def _entry(self, key: str) -> dict:
        return self._cache.get(key) or {
            "fail_count": 0,
            "open_until_epoch_s": 0.0,
            "last_error": "",
        }

    def can_attempt(self, key: str) -> bool:
        entry = self._entry(key)
        return float(entry.get("open_until_epoch_s", 0.0)) <= time.time()

    def record_success(self, key: str) -> None:
        self._cache.set(
            key,
            {
                "fail_count": 0,
                "open_until_epoch_s": 0.0,
                "last_error": "",
                "last_success_epoch_s": time.time(),
            },
        )

    def record_failure(self, key: str, error: str, policy: ReliabilityPolicy) -> None:
        entry = self._entry(key)
        fail_count = int(entry.get("fail_count", 0)) + 1
        open_until = float(entry.get("open_until_epoch_s", 0.0))
        if fail_count >= policy.circuit_fail_threshold:
            open_until = time.time() + policy.circuit_cooldown_s
            fail_count = 0
        self._cache.set(
            key,
            {
                "fail_count": fail_count,
                "open_until_epoch_s": open_until,
                "last_error": error,
                "last_failure_epoch_s": time.time(),
            },
        )


def run_with_reliability[T](
    *,
    key: str,
    policy: ReliabilityPolicy,
    circuit_store: CircuitBreakerStore,
    operation: Callable[[], T],
) -> T:
    """Execute provider operation with retries, timeout, and circuit breaker."""
    if not circuit_store.can_attempt(key):
        raise CircuitOpenError(f"Circuit open for '{key}'. Cooldown in effect.")

    def _run_with_timeout() -> T:
        result_holder: list[T] = []
        error_holder: list[Exception] = []

        def _target() -> None:
            try:
                result_holder.append(operation())
            except Exception as exc:  # noqa: BLE001
                error_holder.append(exc)

        worker = Thread(target=_target, daemon=True)
        worker.start()
        worker.join(timeout=policy.timeout_s)
        if worker.is_alive():
            raise TimeoutError(f"Provider call timed out after {policy.timeout_s}s for '{key}'.")
        if error_holder:
            raise error_holder[0]
        if not result_holder:
            raise RuntimeError(f"Provider call returned no result for '{key}'.")
        return result_holder[0]

    last_error: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            result = _run_with_timeout()
            circuit_store.record_success(key)
            return result
        except TimeoutError as exc:
            last_error = exc
            circuit_store.record_failure(key, str(last_error), policy)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            circuit_store.record_failure(key, str(exc), policy)
        if attempt < policy.max_retries:
            time.sleep(policy.backoff_s * (2**attempt))

    raise ProviderCallError(f"Provider call failed for '{key}': {last_error}")
