"""HTML report generation."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from comicstrip_tutor.storage.io_utils import write_text

_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ComicStrip Tutor Benchmark</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f3f3f3; text-align: left; }
  </style>
</head>
<body>
  <h1>Benchmark {{ benchmark_id }}</h1>
  <table>
    <thead>
      <tr><th>Rank</th><th>Model</th><th>Mean Score</th><th>Total Cost (USD)</th></tr>
    </thead>
    <tbody>
      {% for row in leaderboard %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ row.model_key }}</td>
        <td>{{ "%.4f"|format(row.mean_score) }}</td>
        <td>{{ "%.4f"|format(row.total_cost_usd) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)


def write_html_leaderboard(
    *,
    output_path: Path,
    benchmark_id: str,
    leaderboard: list[dict[str, float | str]],
) -> None:
    """Write HTML leaderboard report."""
    content = _TEMPLATE.render(benchmark_id=benchmark_id, leaderboard=leaderboard)
    write_text(output_path, content)
