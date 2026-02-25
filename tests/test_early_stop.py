from comicstrip_tutor.benchmark.early_stop import should_early_stop


def test_early_stop_false_with_insufficient_samples() -> None:
    assert not should_early_stop(model_scores=[0.3, 0.2], best_mean_so_far=0.8)


def test_early_stop_true_for_weak_model() -> None:
    assert should_early_stop(model_scores=[0.2, 0.25, 0.3], best_mean_so_far=0.8, weak_gap=0.2)
