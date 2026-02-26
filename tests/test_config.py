from comicstrip_tutor.config import AppConfig


def test_experimental_models_enabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("COMIC_TUTOR_ENABLE_EXPERIMENTAL_MODELS", raising=False)
    config = AppConfig.from_env()
    assert config.enable_experimental_models is True


def test_experimental_models_can_be_disabled(monkeypatch) -> None:
    monkeypatch.setenv("COMIC_TUTOR_ENABLE_EXPERIMENTAL_MODELS", "false")
    config = AppConfig.from_env()
    assert config.enable_experimental_models is False
