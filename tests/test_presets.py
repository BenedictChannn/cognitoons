from pathlib import Path

import pytest
from typer.testing import CliRunner

from comicstrip_tutor.cli import app
from comicstrip_tutor.presets import get_preset, list_presets
from comicstrip_tutor.storage.io_utils import read_json

runner = CliRunner()


def test_preset_registry_has_expected_entries() -> None:
    presets = list_presets()
    preset_ids = {preset.preset_id for preset in presets}
    assert {"fast-draft", "publish-strict", "cost-aware-explore"}.issubset(preset_ids)


def test_get_preset_raises_for_unknown() -> None:
    with pytest.raises(KeyError):
        get_preset("unknown")


def test_generate_preset_command_creates_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COMIC_TUTOR_OUTPUT_ROOT", str(tmp_path / "runs"))
    result = runner.invoke(
        app,
        [
            "generate-preset",
            "--preset",
            "fast-draft",
            "--run-id",
            "preset-demo",
            "--topic",
            "Explain CQRS",
        ],
    )
    assert result.exit_code == 0
    run_config = read_json(tmp_path / "runs" / "preset-demo" / "run_config.json")
    assert run_config["template"] == "intuition-to-formalism"
    assert run_config["theme"] == "clean-whiteboard"
