from typer.testing import CliRunner

from comicstrip_tutor.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ComicStrip Tutor" in result.stdout
