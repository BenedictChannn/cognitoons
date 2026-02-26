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

### 2026-02-25 - Live API acceptance run with real keys

**Summary**
- Ran live OpenAI+Gemini API generation for UCT workflow (no dry-run).
- Completed cheap-tier model comparison and benchmark report generation with real API calls.
- Observed persistent timeout/hang behavior for gemini-3-pro-image-preview image generation.

**Details**
- Live artifacts were written under /workspace/live-outputs/experiments to avoid polluting tracked example outputs.
- Gemini 3 Pro Image model hangs on generateContent calls (single-panel and full-strip), even with long timeouts.
- Gemini 2.5 Flash Image and OpenAI GPT Image variants responded successfully.

**Files touched**
- `src/comicstrip_tutor/image_models/gemini_image.py`
- `live-outputs/experiments/live-uct-api`
- `live-outputs/experiments/benchmark-20260225T120525Z`

**Impact**
- Validated live integration path for supported responsive models and exposed premium Gemini runtime blocker.
- Produced fresh live benchmark leaderboard and live comparison artifacts.

**Follow-ups**
- Add configurable per-provider request timeout and retry budget in adapter layer.
- Add graceful skip/fallback when model is available but non-responsive for image generation.

**References**
- run live-uct-api
- benchmark-20260225T120525Z

### 2026-02-25 - Publish curated live-output artifacts to repository

**Summary**
- Curated and prepared successful non-dry-run output artifacts for remote sharing.
- Included live UCT run outputs for gpt-image-1-mini, gemini-2.5-flash-image, and gpt-image-1.5.
- Included live benchmark leaderboard report artifacts for reference.

**Details**
- Only selected successful output folders are being tracked to avoid committing full raw live benchmark payloads.
- README updated to document separate live-output root convention for real API showcase artifacts.

**Files touched**
- `live-outputs/experiments/live-uct-api`
- `live-outputs/experiments/benchmark-20260225T120525Z`
- `README.md`

**Impact**
- Provides concrete real-image evidence in remote branch for review and demos.
- Keeps repository size more controlled than full raw artifact dump.

**Follow-ups**
- Optionally move large binary showcase assets to object storage/CDN in future paid-user setup.

**References**
- run live-uct-api
- benchmark-20260225T120525Z

### 2026-02-26 - Ship critique gating, text policy controls, and provider guardrails

**Summary**
- Added multi-reviewer critique engine with blocking strict mode and persisted critique reports.
- Introduced image_text_mode controls (default none) to reduce in-image text clutter and improve composition readability.
- Added provider reliability policy: timeout, retry, and circuit breaker with persistence.
- Added gemini-3-pro-image-preview fallback to gemini-2.5-flash-image with manifest annotations.
- Integrated Learning Effectiveness Score (LES) into evaluation and benchmark scoring.

**Details**
- Critique reviewers now include technical, beginner, first-year, pedagogy, and visual perspectives with severity-ranked issues and recommendations.
- Render and planning pipelines now run critique, save critique JSON artifacts, and optionally block in strict mode on critical issues.
- Minimal live checkpoint executed on two topics with cheap-tier models and strict critique mode; benchmark checkpoint run on 2 prompts x 2 models.

**Files touched**
- `src/comicstrip_tutor/critique/reviewers.py`
- `src/comicstrip_tutor/critique/orchestrator.py`
- `src/comicstrip_tutor/pipeline/render_pipeline.py`
- `src/comicstrip_tutor/image_models/reliability.py`
- `src/comicstrip_tutor/evaluation/scorer.py`
- `tests/test_critique_engine.py`
- `tests/test_reliability.py`

**Impact**
- Raises quality floor for pedagogical rigor and digestibility before publication.
- Prevents indefinite provider hangs and improves recoverability for premium Gemini instability.
- Shifts benchmark ranking signal toward LES rather than purely structural heuristics.

**Follow-ups**
- Implement explicit template/theme registry artifacts and style-guide compiler next.
- Add automatic panel/storyboard rewrite loop that consumes critique recommendations.

**References**
- commits 40efa55, 9fdd32e, 0adcf34, 52364e9
- checkpoint runs: checkpoint-uct-v2, checkpoint-consistency-v2, benchmark-20260226T061922Z
