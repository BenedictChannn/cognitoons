import time
from pathlib import Path

import pytest

from comicstrip_tutor.image_models.reliability import (
    CircuitBreakerStore,
    CircuitOpenError,
    ReliabilityPolicy,
    run_with_reliability,
)


def test_run_with_reliability_retries_then_succeeds(tmp_path: Path) -> None:
    state = {"calls": 0}

    def flaky() -> str:
        state["calls"] += 1
        if state["calls"] < 2:
            raise RuntimeError("boom")
        return "ok"

    result = run_with_reliability(
        key="provider:model",
        policy=ReliabilityPolicy(
            timeout_s=2,
            max_retries=2,
            backoff_s=0,
            circuit_fail_threshold=3,
            circuit_cooldown_s=10,
        ),
        circuit_store=CircuitBreakerStore(tmp_path / "circuit.json"),
        operation=flaky,
    )
    assert result == "ok"
    assert state["calls"] == 2


def test_run_with_reliability_opens_circuit_after_threshold(tmp_path: Path) -> None:
    store = CircuitBreakerStore(tmp_path / "circuit.json")
    policy = ReliabilityPolicy(
        timeout_s=1,
        max_retries=0,
        backoff_s=0,
        circuit_fail_threshold=1,
        circuit_cooldown_s=120,
    )

    with pytest.raises(RuntimeError):
        run_with_reliability(
            key="provider:model",
            policy=policy,
            circuit_store=store,
            operation=lambda: (_ for _ in ()).throw(RuntimeError("failure")),
        )

    with pytest.raises(CircuitOpenError):
        run_with_reliability(
            key="provider:model",
            policy=policy,
            circuit_store=store,
            operation=lambda: "ok",
        )


def test_run_with_reliability_timeout_returns_promptly(tmp_path: Path) -> None:
    store = CircuitBreakerStore(tmp_path / "circuit.json")
    policy = ReliabilityPolicy(
        timeout_s=0.05,
        max_retries=0,
        backoff_s=0,
        circuit_fail_threshold=3,
        circuit_cooldown_s=10,
    )

    started = time.perf_counter()
    with pytest.raises(RuntimeError, match="timed out"):
        run_with_reliability(
            key="provider:model",
            policy=policy,
            circuit_store=store,
            operation=lambda: time.sleep(2),
        )
    elapsed = time.perf_counter() - started
    assert elapsed < 0.5
