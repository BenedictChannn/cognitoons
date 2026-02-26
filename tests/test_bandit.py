from pathlib import Path

from comicstrip_tutor.exploration.bandit import ExplorationBanditStore


def test_bandit_suggest_prefers_unseen_arm(tmp_path: Path) -> None:
    store = ExplorationBanditStore(tmp_path / "bandit.json")
    store.record(arm_id="a", reward=0.7, cost_usd=0.01)
    suggested = store.suggest_arm(candidate_arms=["a", "b"], exploration_c=1.0)
    assert suggested == "b"


def test_bandit_records_and_reports_mean_reward(tmp_path: Path) -> None:
    store = ExplorationBanditStore(tmp_path / "bandit.json")
    store.record(arm_id="arm", reward=0.5, cost_usd=0.01)
    store.record(arm_id="arm", reward=0.7, cost_usd=0.02)
    stat = store.arm_stats("arm")
    assert stat.pulls == 2
    assert round(stat.mean_reward, 4) == 0.6
