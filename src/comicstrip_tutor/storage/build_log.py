"""Build log maintenance under docs/build-logs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from comicstrip_tutor.storage.io_utils import write_text

BUILD_LOG_DIR = Path("docs/build-logs")
TEMPLATE_PATH = BUILD_LOG_DIR / "_template.md"
INDEX_PATH = BUILD_LOG_DIR / "index.md"


@dataclass(slots=True)
class BuildLogEntry:
    """Structured build log entry."""

    title: str
    summary: list[str]
    details: list[str]
    files_touched: list[str]
    impact: list[str]
    follow_ups: list[str]
    references: list[str]


def slugify(text: str) -> str:
    return "-".join(
        part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
    )


def init_build_log_scaffold() -> None:
    """Ensure build log templates/index exist."""
    BUILD_LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not TEMPLATE_PATH.exists():
        write_text(
            TEMPLATE_PATH,
            "# {{topic}}\n\n## Overview\n- Topic-focused build log.\n\n## Log\n",
        )
    if not INDEX_PATH.exists():
        write_text(INDEX_PATH, "# Build Logs Index\n\n")


def ensure_topic_log(topic: str) -> Path:
    """Create topic log if missing and add to index."""
    init_build_log_scaffold()
    slug = slugify(topic)
    log_path = BUILD_LOG_DIR / f"{slug}.md"
    if not log_path.exists():
        template = TEMPLATE_PATH.read_text(encoding="utf-8").replace("{{topic}}", topic)
        write_text(log_path, template)
        index_content = INDEX_PATH.read_text(encoding="utf-8")
        entry = f"- [{topic}]({slug}.md)\n"
        if entry not in index_content:
            write_text(INDEX_PATH, index_content + entry)
    return log_path


def append_build_log(topic: str, entry: BuildLogEntry) -> Path:
    """Append structured entry to topic log."""
    log_path = ensure_topic_log(topic)
    lines = [
        f"### {date.today().isoformat()} - {entry.title}",
        "",
        "**Summary**",
        *[f"- {bullet}" for bullet in entry.summary],
        "",
        "**Details**",
        *[f"- {bullet}" for bullet in entry.details],
        "",
        "**Files touched**",
        *[f"- `{bullet}`" for bullet in entry.files_touched],
        "",
        "**Impact**",
        *[f"- {bullet}" for bullet in entry.impact],
        "",
        "**Follow-ups**",
        *[f"- {bullet}" for bullet in entry.follow_ups],
        "",
        "**References**",
        *[f"- {bullet}" for bullet in entry.references],
        "",
    ]
    content = log_path.read_text(encoding="utf-8")
    if "## Log" not in content:
        content += "\n## Log\n"
    content += "\n" + "\n".join(lines)
    write_text(log_path, content)
    return log_path
