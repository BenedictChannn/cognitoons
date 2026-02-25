# ComicStrip Tutor App

## Overview
- Tracks implementation milestones, architecture decisions, and experiment outcomes.

## Log

### 2026-02-25 - Bootstrap Python 3.12 + uv architecture

**Summary**
- Initialized Python 3.12 project scaffold with uv-compatible config.
- Implemented core schema, pipeline, model adapter, composition, evaluation, benchmark, and reporting modules.
- Added benchmark dataset (20 items) and build-log infrastructure.

**Details**
- Designed provider-agnostic image model interface and registry for OpenAI/Gemini model families.
- Added explicit planning artifacts and storyboard-first pipeline.
- Implemented dry-run rendering fallback for cost-aware local iteration without API spend.

**Files touched**
- `pyproject.toml`
- `src/comicstrip_tutor/*`
- `benchmark/comic_benchmark_v1.json`
- `docs/build-logs/*`

**Impact**
- Enables end-to-end comic pipeline workflows from CLI.
- Establishes reproducible artifact structure and experiment tracking baseline.

**Follow-ups**
- Add tests and fix lint/type issues.
- Generate sample outputs for at least two topics.
- Expand README with acceptance-test walkthrough commands.

**References**
- Branch: `cursor/comic-strip-tutor-app-0f13`

### 2026-02-25 - Run dry-run demos and benchmark outputs

**Summary**
- Generated two topic examples with cheap/premium comparisons
- Executed single-panel reroll for UCT panel #3
- Ran 10-item benchmark and produced leaderboard reports

**Details**
- All runs used dry-run rendering to avoid API costs while preserving artifact structure.
- Experiment outputs stored under examples/outputs for reproducible walkthroughs.

**Files touched**
- `examples/outputs/topic-uct`
- `examples/outputs/topic-rl-exploration`
- `examples/outputs/benchmark-20260225T105101Z`

**Impact**
- Provides ready-to-review artifacts for acceptance demos.
- Confirms benchmark/report and comparison pipelines work end-to-end.

**Follow-ups**
- Optionally rerun demos with live API keys for real model images.

**References**
- benchmark-20260225T105101Z

### 2026-02-25 - Fix experiment registry scoping and README CLI commands

**Summary**
- Scoped experiment registry writes to output-root parent to prevent test pollution.
- Corrected README acceptance commands to use positional run_id for render/reroll/compare.

**Details**
- Previously, registry writes always targeted runs/experiment_registry.jsonl regardless of configured output root.
- Added regression test to verify registry file location for custom output roots.

**Files touched**
- `src/comicstrip_tutor/storage/artifact_store.py`
- `tests/test_artifact_store.py`
- `README.md`

**Impact**
- Improves artifact hygiene and reproducibility for tests/custom output paths.
- Keeps docs aligned with actual CLI behavior.

**Follow-ups**
- Optional: add an explicit --run-id option alias for render/compare/reroll commands.

**References**
- commit eb3ab8f

### 2026-02-25 - Add panel-image cache reuse for reproducible rerenders

**Summary**
- Implemented prompt+model keyed panel cache to reuse prior panel outputs.
- Render pipeline now records cache-hit metadata and zero incremental estimated cost for hits.
- Added integration test proving second render of same storyboard/model costs zero estimated dollars.

**Details**
- Cache key includes model, mode, size, style guide, and panel prompt text hash input to keep comparisons fair and deterministic.
- Cache is stored at output-root parent (panel_cache.json), parallel to experiment registry.

**Files touched**
- `src/comicstrip_tutor/pipeline/render_pipeline.py`
- `tests/integration/test_render_cache_reuse.py`
- `README.md`

**Impact**
- Faster iteration on unchanged storyboards and cleaner cost-aware experimentation loops.
- Improves reproducibility when comparing models on identical prompts.

**Follow-ups**
- Consider cache eviction policy for very large local artifact stores.

**References**
- commit d48defc
