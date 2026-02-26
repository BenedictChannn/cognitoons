# Live Output Artifacts

This directory stores curated **real API** run outputs intended for remote review.

Included:
- `experiments/live-uct-api/` (successful live run showcase)
  - composite strip outputs for supported models
  - side-by-side comparison image
  - manifests/evaluations/storyboard/planning metadata
- `experiments/live-lockfree-v4/` (strict critique + rewrite policy live showcase)
  - strict critique artifacts with issue codes and rewrite iteration logs
  - publish-mode composites for `gpt-image-1-mini` and `gemini-2.5-flash-image`
  - evaluation artifacts with LES + publishability verdicts
- `experiments/benchmark-20260225T120525Z/` (live benchmark leaderboard report)
- `experiments/benchmark-20260226T092918Z/` (live benchmark with updated gate diagnostics)
- `experiments/live-nano-pro-v1/` (Nano Banana Pro live compare checkpoint)
  - successful live render + compare for:
    - `gemini-3-pro-image-preview`
    - `gemini-2.5-flash-image`
  - includes manifests, evaluations, critique artifacts, and compare composite
- `experiments/probe-gemini-3-pro-image-preview-20260226t171944z/`
  - 5/5 successful IMAGE-only probes
  - response diagnostics show inline image parts present in every attempt
- `experiments/probe-gemini-3.1-flash-image-preview-20260226t173533z/`
  - 0/5 successful probes
  - two timeout failures followed by circuit-open failures (guardrail activation)
  - currently treated as experimental / not production-ready

Not included:
- Full raw live benchmark per-item payloads (kept local during development to limit repo bloat).
