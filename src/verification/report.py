from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.replication_paths import APPENDIX_FIGURES, OUTPUTS, PAPER_FIGURES, TABLES
from src.verification.correspondence import ARTIFACTS


def _escape(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _status_badge(check: dict[str, Any]) -> str:
    if check.get("skipped"):
        return '<span class="badge skipped">Skipped</span>'
    if check.get("pass"):
        return '<span class="badge pass">Pass</span>'
    return '<span class="badge fail">Fail</span>'


def _dict_table(values: dict[str, Any]) -> str:
    rows = []
    for key, value in values.items():
        if isinstance(value, dict):
            value = json.dumps(value, indent=2)
        rows.append(f"<tr><th>{_escape(key)}</th><td><pre>{_escape(value)}</pre></td></tr>")
    return "<table>" + "\n".join(rows) + "</table>"


def _checks_table(checks: list[dict[str, Any]]) -> str:
    rows = [
        "<tr><th>Status</th><th>Check</th><th>Actual</th><th>Expected</th></tr>",
    ]
    for check in checks:
        rows.append(
            "<tr>"
            f"<td>{_status_badge(check)}</td>"
            f"<td>{_escape(check.get('check'))}</td>"
            f"<td><pre>{_escape(json.dumps(check.get('actual'), indent=2) if isinstance(check.get('actual'), (dict, list)) else check.get('actual'))}</pre></td>"
            f"<td><pre>{_escape(json.dumps(check.get('expected'), indent=2) if isinstance(check.get('expected'), (dict, list)) else check.get('expected'))}</pre></td>"
            "</tr>"
        )
    return "<table>" + "\n".join(rows) + "</table>"


def _coef_table(path: Path, title: str) -> str:
    if not path.exists():
        return f"<h3>{_escape(title)}</h3><p>Not generated.</p>"

    df = pd.read_csv(path)
    sections: list[str] = [f"<h3>{_escape(title)}</h3>"]
    for table_id, group in df.groupby("table_id", sort=False):
        formatted = group.copy()
        formatted["estimate"] = formatted.apply(
            lambda row: f"{row['coefficient']:.3f}"
            + (f" ({row['std_error']:.3f})" if pd.notna(row.get("std_error")) else ""),
            axis=1,
        )
        pivot = formatted.pivot_table(
            index="term",
            columns="model",
            values="estimate",
            aggfunc="first",
            sort=False,
        ).fillna("")
        sections.append(f"<h4>{_escape(table_id)}</h4>")
        sections.append(pivot.to_html(classes="dataframe", escape=True))
    return "\n".join(sections)


def _summary_table(path: Path) -> str:
    if not path.exists():
        return "<h3>Supplement Table A.1</h3><p>Not generated.</p>"

    df = pd.read_csv(path)
    df["value"] = df.apply(lambda row: f"{row['mean']:.3f} ({row['std_dev']:.3f})", axis=1)
    pivot = df.pivot_table(
        index="variable",
        columns="treatment",
        values="value",
        aggfunc="first",
        sort=False,
    ).fillna("")
    observations = df.groupby("treatment", sort=False)["observations"].first()
    pivot.loc["N"] = observations.astype(str)
    return "<h3>Supplement Table A.1: Summary Statistics</h3>" + pivot.to_html(
        classes="dataframe", escape=True
    )


def _artifact_table() -> str:
    rows = ["<tr><th>Paper artifact</th><th>Script</th><th>Generated output</th><th>Status</th></tr>"]
    for artifact in ARTIFACTS:
        rows.append(
            "<tr>"
            f"<td>{_escape(artifact.paper_artifact)}</td>"
            f"<td><code>{_escape(artifact.source)}</code></td>"
            f"<td><code>{_escape(artifact.output)}</code></td>"
            f"<td>{_escape(artifact.status)}</td>"
            "</tr>"
        )
    return "<table>" + "\n".join(rows) + "</table>"


def _figure_gallery() -> str:
    paths = [*sorted(PAPER_FIGURES.glob("*.png")), *sorted(APPENDIX_FIGURES.glob("*.png"))]
    if not paths:
        return "<p>No figures generated.</p>"
    items = []
    for path in paths:
        rel = Path(os.path.relpath(path, OUTPUTS)).as_posix()
        items.append(
            "<figure>"
            f'<a href="{_escape(rel)}"><img src="{_escape(rel)}" alt="{_escape(path.name)}"></a>'
            f"<figcaption>{_escape(path.name)}</figcaption>"
            "</figure>"
        )
    return '<div class="gallery">' + "\n".join(items) + "</div>"


def build_report(
    setup: dict[str, Any],
    verification: dict[str, Any] | None,
    mode: str,
    stata_tables_rerun: bool,
) -> str:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    pass_status = verification.get("pass") if verification else None
    status_text = "Passed" if pass_status else "Failed" if pass_status is False else "Setup only"
    checks_html = _checks_table(verification.get("checks", [])) if verification else "<p>No diagnostic checks were run.</p>"

    body = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Efficiency Wages Analysis Diagnostics</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; color: #222; }}
    h1, h2, h3, h4 {{ line-height: 1.25; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; font-size: 0.92rem; }}
    th, td {{ border: 1px solid #d0d7de; padding: 0.45rem 0.6rem; vertical-align: top; }}
    th {{ background: #f6f8fa; text-align: left; }}
    pre {{ margin: 0; white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 0.4rem; font-weight: 600; }}
    .pass {{ background: #dafbe1; color: #116329; }}
    .fail {{ background: #ffebe9; color: #82071e; }}
    .skipped {{ background: #fff8c5; color: #6e4f00; }}
    .notice {{ background: #f6f8fa; border-left: 4px solid #57606a; padding: 0.75rem 1rem; }}
    .gallery {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }}
    figure {{ margin: 0; border: 1px solid #d0d7de; padding: 0.75rem; }}
    img {{ max-width: 100%; height: auto; }}
    figcaption {{ margin-top: 0.5rem; font-size: 0.85rem; color: #57606a; }}
  </style>
</head>
<body>
  <h1>Efficiency Wages with Motivated Agents: Analysis Diagnostics</h1>
  <p class="notice">Run mode: <strong>{_escape(mode)}</strong>. Overall status: <strong>{_escape(status_text)}</strong>. Stata tables rerun in this report: <strong>{_escape(stata_tables_rerun)}</strong>.</p>

  <h2>Setup</h2>
  {_dict_table(setup)}

  <h2>Diagnostic Checks</h2>
  {checks_html}

  <h2>Analysis Artifact Map</h2>
  {_artifact_table()}

  <h2>Generated Tables</h2>
  {_summary_table(TABLES / "appendix_table_a1_summary_statistics.csv")}
  {_coef_table(TABLES / "main_tables_results.csv", "Main Regression Tables")}
  {_coef_table(TABLES / "appendix_tables_results.csv", "Appendix Regression Tables")}

  <h2>Generated Figures</h2>
  {_figure_gallery()}
</body>
</html>
"""
    output = OUTPUTS / "diagnostics.html"
    output.write_text(body)
    return str(output)
