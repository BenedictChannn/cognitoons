# ComicStrip Tutor

ComicStrip Tutor is a **comic-specific teaching pipeline** for technical topics.

It is intentionally not a one-shot image generator. It uses explicit intermediate artifacts:

1. learning plan + misconceptions
2. story arc
3. storyboard (editable)
4. per-panel generation
5. strip composition
6. comic-specific evaluation + benchmarking

---

## Features

- Topic input (`--topic`) and source-content input (`--source-text` / `--source-file`)
- Editable storyboard before rendering
- Single-panel reroll (`reroll-panel`) without rerendering everything
- Model comparison on same storyboard (`compare`)
- Benchmark harness with cheap→expensive model ordering + early-stop
- Multi-reviewer critique gate (technical + beginner + first-year + pedagogy + visual)
- `image_text_mode` controls (`none|minimal|full`) with production default `none`
- Automatic critique-driven storyboard rewrite loop (`--auto-rewrite`)
- Cost estimate + usage metadata capture
- Reliability guardrails (timeout, retry, circuit breaker) + Gemini 3 fallback
- Exploration-vs-exploitation scaffolding via persistent UCB bandit arm stats
- Prompt/image cache reuse for reproducible model comparisons
- Build logs under `docs/build-logs/`
- Experiment artifacts under `runs/experiments/`

---

## Supported image models

OpenAI:
- `gpt-image-1-mini`
- `gpt-image-1`
- `gpt-image-1.5`

Gemini:
- `gemini-2.5-flash-image`
- `gemini-3-pro-image-preview`

---

## Quickstart (Python 3.12 + uv)

```bash
python3.12 --version
~/.local/bin/uv sync
```

Create env file:

```bash
cp .env.example .env
```

Set keys (optional for live API runs):

```dotenv
OPENAI_API_KEY=...
GEMINI_API_KEY=...
COMIC_TUTOR_OUTPUT_ROOT=runs/experiments
```

Run CLI:

```bash
~/.local/bin/uv run comic-tutor --help
```

---

## CLI Commands

```bash
comic-tutor list-models
comic-tutor list-templates
comic-tutor list-themes
comic-tutor suggest-arm [--models ... --templates ... --themes ... --text-modes ...]
comic-tutor bandit-stats [--limit 10]
comic-tutor rate-run <run_id> --model <model_key> --rating 1..5 [--note "..."]
comic-tutor generate --topic "..." [--panel-count 6] [--mode draft|publish] [--template ...] [--theme ...]
comic-tutor edit-storyboard <run_id> [--open-editor]
comic-tutor render <run_id> --model <model_key> [--dry-run] [--critique-mode off|warn|strict] [--image-text-mode none|minimal|full]
comic-tutor reroll-panel <run_id> --model <model_key> --panel 3 --metaphor "..."
comic-tutor compare <run_id> --model-a <A> --model-b <B> [--dry-run]
comic-tutor benchmark --dataset benchmark/comic_benchmark_v1.json --limit 10 [--dry-run]
comic-tutor report --benchmark-run <benchmark_id>
comic-tutor build-log --intent create|update --topic "..." --title "..."
```

---

## Acceptance test demo walkthrough

> Use `~/.local/bin/uv run` prefix for all commands below.

### 1) Generate 6-panel UCT comic with recap

```bash
comic-tutor generate \
  --run-id demo-uct \
  --topic "Explain UCT in MCTS to a beginner" \
  --panel-count 6 \
  --mode draft \
  --critique-mode strict \
  --auto-rewrite \
  --critique-max-iterations 2 \
  --image-text-mode none \
  --template intuition-to-formalism \
  --theme clean-whiteboard
comic-tutor render demo-uct --model gpt-image-1-mini --mode draft --dry-run --critique-mode strict --image-text-mode none
```

### 2) Regenerate only panel #3 with new metaphor

```bash
comic-tutor reroll-panel \
  demo-uct \
  --model gpt-image-1-mini \
  --panel 3 \
  --metaphor "Tree search is like trying hallways in a maze with a confidence scoreboard" \
  --mode draft \
  --dry-run
```

### 3) Compare same storyboard: `gpt-image-1-mini` vs `gemini-2.5-flash-image`

```bash
comic-tutor compare \
  demo-uct \
  --model-a gpt-image-1-mini \
  --model-b gemini-2.5-flash-image \
  --mode draft \
  --dry-run
```

### 4) Compare premium: `gpt-image-1.5` vs `gemini-3-pro-image-preview`

```bash
comic-tutor compare \
  demo-uct \
  --model-a gpt-image-1.5 \
  --model-b gemini-3-pro-image-preview \
  --mode publish \
  --dry-run
```

### 5) Benchmark on >=10 prompts with leaderboard

```bash
comic-tutor benchmark \
  --dataset benchmark/comic_benchmark_v1.json \
  --limit 10 \
  --models cheap-first \
  --mode draft \
  --dry-run
```

Then:

```bash
comic-tutor report --benchmark-run <printed-benchmark-id>
```

---

## Output artifacts

Per run (`runs/experiments/<run_id>/`):

- `run_config.json`
- `planning/learning_plan.json`
- `planning/story_arc.json`
- `planning/characters.json`
- `planning/style_guide.json`
- `storyboard.json`
- `storyboard_meta.json`
- `critique/post_planning.json`
- `critique/pre_render_<model>.json`
- `panel_prompts/panel_XX.txt`
- `images/<model>/panel_XX.png`
- `composite/<model>/strip.png` and `.pdf`
- `evaluation/<model>.json`
- `manifest_<model>.json`

Global:
- `<output_root_parent>/experiment_registry.jsonl` (default: `runs/experiment_registry.jsonl`)
- `<output_root_parent>/panel_cache.json` (prompt+model cache for panel reuse)
- `<output_root_parent>/provider_circuit.json` (provider/model circuit-breaker state)
- `<output_root_parent>/exploration_bandit.json` (arm pulls/reward aggregates)
- benchmark reports under `runs/experiments/<benchmark_id>/leaderboard.{md,html}`
  - leaderboard now includes LES/comprehension/rigor/publish-gate and top gate failures

Live showcase artifacts (real API runs) can be kept in a separate output root,
for example:

- `live-outputs/experiments/live-uct-api/`
- `live-outputs/experiments/benchmark-<timestamp>/`

---

## Benchmark dataset

`benchmark/comic_benchmark_v1.json` contains 20 items with:

```json
{
  "id": "string",
  "topic": "string",
  "audience_level": "beginner|intermediate|advanced",
  "expected_key_points": ["..."],
  "common_misconceptions": ["..."]
}
```

---

## Development checks

```bash
~/.local/bin/uv run ruff check .
~/.local/bin/uv run ruff format .
~/.local/bin/uv run ty check .
~/.local/bin/uv run pytest -q
```

---

## Build logs

- Build logs live in `docs/build-logs/`.
- Use the `build-log` command to create/update topic logs.
- `docs/build-logs/comicstrip-tutor-app.md` tracks major milestones for this app.
