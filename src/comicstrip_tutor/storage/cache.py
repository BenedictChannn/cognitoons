"""Prompt/cache utilities."""

from __future__ import annotations

from pathlib import Path

from comicstrip_tutor.storage.io_utils import ensure_parent, read_json, write_json


class JsonCache:
    """Very small JSON-file key-value cache."""

    def __init__(self, path: Path):
        self.path = path
        ensure_parent(path)
        if not path.exists():
            write_json(path, {})

    def get(self, key: str) -> dict | None:
        data = read_json(self.path)
        return data.get(key)

    def set(self, key: str, value: dict) -> None:
        data = read_json(self.path)
        data[key] = value
        write_json(self.path, data)
