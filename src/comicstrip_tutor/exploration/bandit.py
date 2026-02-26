"""Multi-armed bandit scaffolding for exploration vs exploitation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from comicstrip_tutor.storage.cache import JsonCache


@dataclass(slots=True, frozen=True)
class ArmStats:
    """Aggregated reward stats for one arm."""

    arm_id: str
    pulls: int
    total_reward: float
    total_cost_usd: float

    @property
    def mean_reward(self) -> float:
        if self.pulls <= 0:
            return 0.0
        return self.total_reward / self.pulls


class ExplorationBanditStore:
    """Persistent UCB1-style arm scorer."""

    def __init__(self, path: Path):
        self.path = path
        self.cache = JsonCache(path)

    def _state(self) -> dict:
        return self.cache.get("arms") or {}

    def arm_stats(self, arm_id: str) -> ArmStats:
        state = self._state()
        item = state.get(arm_id, {})
        return ArmStats(
            arm_id=arm_id,
            pulls=int(item.get("pulls", 0)),
            total_reward=float(item.get("total_reward", 0.0)),
            total_cost_usd=float(item.get("total_cost_usd", 0.0)),
        )

    def record(self, *, arm_id: str, reward: float, cost_usd: float) -> None:
        state = self._state()
        current = state.get(arm_id, {"pulls": 0, "total_reward": 0.0, "total_cost_usd": 0.0})
        state[arm_id] = {
            "pulls": int(current["pulls"]) + 1,
            "total_reward": float(current["total_reward"]) + reward,
            "total_cost_usd": float(current["total_cost_usd"]) + cost_usd,
        }
        self.cache.set("arms", state)

    def all_stats(self) -> list[ArmStats]:
        state = self._state()
        return [
            ArmStats(
                arm_id=arm_id,
                pulls=int(item.get("pulls", 0)),
                total_reward=float(item.get("total_reward", 0.0)),
                total_cost_usd=float(item.get("total_cost_usd", 0.0)),
            )
            for arm_id, item in state.items()
        ]

    def suggest_arm(self, *, candidate_arms: list[str], exploration_c: float = 1.2) -> str:
        if not candidate_arms:
            raise ValueError("candidate_arms cannot be empty.")
        stats = {arm: self.arm_stats(arm) for arm in candidate_arms}
        unseen = [arm for arm, stat in stats.items() if stat.pulls == 0]
        if unseen:
            return unseen[0]

        total_pulls = sum(stat.pulls for stat in stats.values())
        if total_pulls <= 0:
            return candidate_arms[0]

        best_arm = candidate_arms[0]
        best_value = float("-inf")
        for arm in candidate_arms:
            stat = stats[arm]
            exploitation = stat.mean_reward
            exploration = exploration_c * math.sqrt(math.log(total_pulls) / stat.pulls)
            ucb = exploitation + exploration
            if ucb > best_value:
                best_value = ucb
                best_arm = arm
        return best_arm
