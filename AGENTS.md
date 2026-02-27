# AGENTS.md

## Cursor Cloud specific instructions

**Product**: ComicStrip Tutor — a Python CLI pipeline that generates educational comic strips for technical topics using AI image models. Pure CLI, no web server or database.

### Quick reference

- **Language**: Python 3.12 (`uv` package manager, lockfile: `uv.lock`)
- **CLI entry point**: `uv run comic-tutor <command>`
- **Dev checks** (see `README.md § Development checks`):
  - Lint: `uv run ruff check .`
  - Format: `uv run ruff format --check .` (auto-fix: `uv run ruff format .`)
  - Type check: `uv run ty check .`
  - Tests: `uv run pytest -q`
- **All tests run offline** — no API keys needed. Tests mock all external providers.

### Running the app without API keys

All CLI commands that hit external APIs (`render`, `compare`, `benchmark`, `probe-model`) accept a `--dry-run` flag that generates placeholder images locally. Use this for end-to-end validation without `OPENAI_API_KEY` / `GEMINI_API_KEY`.

Example hello-world dry-run:

```bash
uv run comic-tutor generate --run-id test-run --topic "Explain recursion" --panel-count 6 --mode draft --critique-mode off --image-text-mode none --template intuition-to-formalism --theme clean-whiteboard
uv run comic-tutor render test-run --model gpt-image-1-mini --mode draft --dry-run --critique-mode off --image-text-mode none
```

Artifacts land in `runs/experiments/<run_id>/`.

### Non-obvious caveats

- The `.env` file must exist (copy from `.env.example`) even when running dry-run commands, because `python-dotenv` is loaded on import.
- `uv` must be on `PATH` — installed to `~/.local/bin` by default. The VM snapshot already has it.
- Commit rules require running `ruff check .`, `ruff format .`, and `ty check .` before committing (see `.cursor/rules/commit-cadence.mdc`).
