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

Not included:
- Full raw live benchmark per-item payloads (kept local during development to limit repo bloat).
