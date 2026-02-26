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

### 2026-02-26 - Add style-guide compiler and template/theme registries

**Summary**
- Implemented explicit template registry and theme registry with CLI discovery commands.
- Planner now compiles template+theme into planning/style_guide.json and embeds constraints in storyboard style guide text.
- Added strict fallback path for gemini-3-pro-image-preview to gemini-2.5-flash-image with manifest notes.

**Details**
- New commands: list-templates, list-themes for discoverability and controlled exploration.
- Storyboard schema now captures template and theme identifiers for reproducibility.
- Added tests for style compiler and gemini fallback integration path.

**Files touched**
- `src/comicstrip_tutor/styles/compiler.py`
- `src/comicstrip_tutor/styles/templates.py`
- `src/comicstrip_tutor/styles/themes.py`
- `src/comicstrip_tutor/pipeline/planner_pipeline.py`
- `src/comicstrip_tutor/pipeline/render_pipeline.py`

**Impact**
- Improves exploration-vs-exploitation workflow with deterministic style artifacts.
- Reduces production risk from gemini-3 hang by enabling graceful panel fallback.

**Follow-ups**
- Implement critique-driven automatic rewrite loop that mutates storyboard before render.
- Add LES-specific leaderboard columns in markdown/html reports.

**References**
- commits 7796e54, b5e5023, 52364e9

### 2026-02-26 - Add critique rewrite loop, LES publishability gates, and exploration bandit scaffolding

**Summary**
- Implemented automatic critique-driven storyboard rewrite loop with iteration artifacts and strict blocking when unresolved issues persist.
- Extended evaluation with publishability verdict and reasons based on LES/comprehension/rigor thresholds.
- Upgraded benchmark leaderboard/reporting to expose LES, comprehension, rigor, and publish-gate pass rate.
- Added persistent UCB exploration bandit store with CLI commands to suggest next arm and inspect arm stats.

**Details**
- Planning and pre-render critique pipelines now persist per-iteration critique and rewrite-note artifacts.
- Render publish mode now enforces strict publishability gates (LES >= 0.80, comprehension >= 0.80, rigor >= 0.95 + structural checks).
- Benchmark runner now records exploration arm outcomes into exploration_bandit.json for future exploit/explore policy.

**Files touched**
- `src/comicstrip_tutor/pipeline/critique_pipeline.py`
- `src/comicstrip_tutor/critique/rewrite.py`
- `src/comicstrip_tutor/evaluation/scorer.py`
- `src/comicstrip_tutor/benchmark/leaderboard.py`
- `src/comicstrip_tutor/exploration/bandit.py`
- `src/comicstrip_tutor/cli.py`

**Impact**
- Moves critique from advisory-only to iterative quality-improvement loop with measurable exit gates.
- Improves benchmark signal alignment with learning outcomes and release readiness.
- Introduces data foundation for exploration-vs-exploitation arm policy optimization.

**Follow-ups**
- Add report-level visual diagnostics explaining why publish gate failed per run/model.
- Feed user preference ratings into bandit reward shaping.

**References**
- commits d3d5a74, 0ab9172
- checkpoint runs: checkpoint-rewrite-v3, benchmark-20260226T071211Z, benchmark-20260226T071507Z

### 2026-02-26 - Harden critique semantics + add feedback reward loop + publish live strict showcase

**Summary**
- Replaced brittle rewrite string matching with structured critique issue codes and metadata payloads.
- Added user feedback loop via rate-run command; ratings now update exploration bandit rewards with LES blending.
- Extended benchmark diagnostics with top publish-gate failure reasons in CLI, markdown, and HTML reports.
- Published new live strict-critique showcase run (lock-free stack/ABA) with two real models and comparison.

**Details**
- Critique issue taxonomy now drives rewrite logic deterministically and is resilient to message wording changes.
- Added canonical arm-id helper and integrated it across benchmark arm recording, suggestion, and user rating updates.
- Live run live-lockfree-v4 passed strict critique and publishability gates with LES 0.9615 on both cheap-tier models.

**Files touched**
- `src/comicstrip_tutor/schemas/critique.py`
- `src/comicstrip_tutor/critique/reviewers.py`
- `src/comicstrip_tutor/critique/rewrite.py`
- `src/comicstrip_tutor/cli.py`
- `src/comicstrip_tutor/benchmark/leaderboard.py`
- `src/comicstrip_tutor/exploration/arms.py`
- `live-outputs/experiments/live-lockfree-v4/`

**Impact**
- Removes brittle text-coupling in core quality rewrite loop and improves long-term maintainability.
- Introduces preference-aware reward shaping foundation for exploration policy decisions.
- Improves reviewer transparency by surfacing publish-gate failure diagnostics in benchmark outputs.

**Follow-ups**
- Expand issue-code taxonomy for future LLM-based reviewers and enforce code coverage in tests.
- Start weighting bandit reward with explicit user cohort preferences once data volume grows.

**References**
- commits 84168d9, 4208d52, d2beb11
- live run: live-lockfree-v4

### 2026-02-26 - Add render error taxonomy and completion-state guarantees

**Summary**
- Render pipeline now classifies failures into stable error taxonomy keys (timeout, circuit open, schema failure, etc.).
- Render manifests now persist completion status (success/partial_success/failure) with error_type and error_message for diagnostics.
- Failure paths now still write manifest and registry failure events, improving post-mortem traceability.

**Details**
- Added error classification helper module and tests for taxonomy behavior.
- Added integration test proving manifest persistence on provider timeout failure.

**Files touched**
- `src/comicstrip_tutor/pipeline/error_taxonomy.py`
- `src/comicstrip_tutor/pipeline/render_pipeline.py`
- `src/comicstrip_tutor/schemas/runs.py`
- `tests/integration/test_render_failure_manifest.py`

**Impact**
- Improves reliability observability and fulfills run-state guarantee requirement with actionable diagnostics.

**Follow-ups**
- Add run-level dashboard/report section summarizing failure taxonomy distribution over time.

**References**
- commit d9df218

### 2026-02-26 - Add onboarding presets and per-run quality report UX

**Summary**
- Added preset registry and CLI commands (list-presets, generate-preset) for faster onboarding and repeatable workflows.
- Added quality-report command and markdown report artifact per run/model with publishability and critique issue diagnostics.
- Updated render pipeline to auto-write quality reports after render completion/failure for easier review.

**Details**
- Presets include fast-draft, publish-strict, and cost-aware-explore with curated default configuration.
- Quality report includes completion status, LES/comprehension/rigor, publishability reasons, and structured critique issue table.

**Files touched**
- `src/comicstrip_tutor/presets.py`
- `src/comicstrip_tutor/reporting/quality_report.py`
- `src/comicstrip_tutor/cli.py`
- `src/comicstrip_tutor/pipeline/render_pipeline.py`
- `tests/test_presets.py`
- `tests/test_quality_report.py`

**Impact**
- Improves paid-user onboarding and shortens path to first quality output.
- Makes pass/fail reasons transparent for each run, improving trust and debuggability.

**Follow-ups**
- Add themed preset packs by topic domain (systems, ML, backend, frontend).

**References**
- commits 94d0440, 553600d
- checkpoint runs: checkpoint-quality-report-v5, checkpoint-preset-v1

### 2026-02-26 - Finish onboarding/report polish and recalibrate rigor gate diagnostics

**Summary**
- Added list-presets and generate-preset commands with curated preset registry for faster onboarding.
- Added per-run quality report generation command and auto-generated quality markdown after render.
- Refined technical rigor scoring to penalize issue codes proportionally and improved publish-gate pass alignment.
- Published new live benchmark diagnostics checkpoint with updated gate-failure columns.

**Details**
- Benchmark CLI now supports explicit --dry-run/--live toggle; validated via live benchmark run.
- Dry benchmark pass-rate on 5-item subset improved from 0.20 to 0.60 after rigor scoring calibration.
- Live benchmark checkpoint benchmark-20260226T092918Z produced LES 0.9720 and publish-gate pass 1.0 on sampled item.

**Files touched**
- `src/comicstrip_tutor/presets.py`
- `src/comicstrip_tutor/reporting/quality_report.py`
- `src/comicstrip_tutor/evaluation/scorer.py`
- `src/comicstrip_tutor/cli.py`
- `live-outputs/experiments/benchmark-20260226T092918Z/`

**Impact**
- Improves first-run product onboarding and transparency of run-level quality outcomes.
- Makes benchmark diagnostics more actionable and better aligned with learning-quality goals.

**Follow-ups**
- Expand preset catalog by domain and attach recommended model tiers per preset.

**References**
- commits 94d0440, 553600d, 651bd1b, 4d22e52
