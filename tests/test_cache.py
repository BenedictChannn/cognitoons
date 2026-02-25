from pathlib import Path

from comicstrip_tutor.storage.cache import JsonCache


def test_json_cache_roundtrip(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path / "cache.json")
    assert cache.get("missing") is None
    cache.set("k1", {"a": 1})
    assert cache.get("k1") == {"a": 1}
