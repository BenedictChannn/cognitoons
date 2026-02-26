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
      <tr>
        <th>Rank</th>
        <th>Model</th>
        <th>Mean LES</th>
        <th>Mean Score</th>
        <th>Mean Comprehension</th>
        <th>Mean Rigor</th>
        <th>Publish Gate Pass</th>
        <th>Top Gate Failures</th>
        <th>Total Cost (USD)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in leaderboard %}
      {% set publish_pass = row.publish_gate_pass_rate
        if row.publish_gate_pass_rate is defined else 0.0 %}
      {% set top_failures = row.top_gate_failures if row.top_gate_failures is defined else "none" %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ row.model_key }}</td>
        <td>
          {{ "%.4f"|format(row.mean_les if row.mean_les is defined else row.mean_score) }}
        </td>
        <td>{{ "%.4f"|format(row.mean_score) }}</td>
        <td>
          {{ "%.4f"|format(row.mean_comprehension if row.mean_comprehension is defined else 0.0) }}
        </td>
        <td>{{ "%.4f"|format(row.mean_rigor if row.mean_rigor is defined else 0.0) }}</td>
        <td>{{ "%.4f"|format(publish_pass) }}</td>
        <td>{{ top_failures }}</td>
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
