from pathlib import Path

from comicstrip_tutor.schemas.runs import RunConfig
from comicstrip_tutor.storage.artifact_store import ArtifactStore


def test_registry_path_scoped_to_output_root_parent(tmp_path: Path) -> None:
    output_root = tmp_path / "runs" / "experiments"
    store = ArtifactStore(output_root=output_root)
    run_config = RunConfig(run_id="scope-test", topic="topic", panel_count=4, mode="draft")
    store.create_run(run_config)
    store.append_registry({"run_id": "scope-test", "event": "planning_complete"})
    expected_registry = tmp_path / "runs" / "experiment_registry.jsonl"
    assert expected_registry.exists()
    assert "scope-test" in expected_registry.read_text(encoding="utf-8")
