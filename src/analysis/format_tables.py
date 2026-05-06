from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

import pandas as pd

from src.replication_paths import APPENDIX_TABLES, PAPER_TABLES, TABLES


TABLE_NAMES = {
    "Table 2": "table_2_acceptance",
    "Table 3": "table_3_effort",
    "Table 4": "table_4_wage_offers",
    "Table A.1": "table_a1_summary_statistics",
    "Table A.2": "table_a2_effort_ge_prosocial",
    "Table A.3": "table_a3_effort_neutral_efficiency",
    "Table A.4": "table_a4_acceptance_neutral",
    "Table A.5": "table_a5_acceptance_efficiency",
    "Table A.6": "table_a6_effort_neutral",
    "Table A.7": "table_a7_effort_efficiency",
    "Table A.8": "table_a8_wage_offers_neutral",
    "Table A.9": "table_a9_wage_offers_efficiency",
}


def _p_value(coefficient: float, std_error: float) -> float | None:
    if not math.isfinite(coefficient) or not math.isfinite(std_error) or std_error == 0:
        return None
    statistic = abs(coefficient / std_error)
    return 2 * (1 - NormalDist().cdf(statistic))


def _stars(p_value: float | None) -> str:
    if p_value is None:
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.1:
        return "*"
    return ""


def _fmt_number(value: float | int | None, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def _latex_escape(value: object) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _write_latex(df: pd.DataFrame, path: Path) -> None:
    cols = list(df.columns)
    lines = [
        r"\begin{tabular}{l" + "c" * (len(cols) - 1) + "}",
        r"\hline",
        " & ".join(_latex_escape(col) for col in cols) + r" \\",
        r"\hline",
    ]
    for _, row in df.iterrows():
        lines.append(" & ".join(_latex_escape(row[col]) for col in cols) + r" \\")
    lines.extend([r"\hline", r"\end{tabular}", ""])
    path.write_text("\n".join(lines))


def _add_p_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["p_value"] = df.apply(
        lambda row: _p_value(float(row["coefficient"]), float(row["std_error"]))
        if pd.notna(row.get("coefficient")) and pd.notna(row.get("std_error"))
        else None,
        axis=1,
    )
    return df


def _formatted_regression_table(group: pd.DataFrame) -> pd.DataFrame:
    group = _add_p_values(group)
    models = list(dict.fromkeys(group["model"].astype(str)))
    rows: list[dict[str, str]] = []

    for term in dict.fromkeys(group["term"]):
        coef_row = {"Term": term}
        se_row = {"Term": ""}
        for model in models:
            match = group[(group["model"].astype(str) == model) & (group["term"] == term)]
            if match.empty:
                coef_row[model] = ""
                se_row[model] = ""
                continue
            row = match.iloc[0]
            p_value = row.get("p_value")
            coef_row[model] = _fmt_number(row["coefficient"]) + _stars(p_value)
            se_row[model] = f"({_fmt_number(row['std_error'])})" if pd.notna(row["std_error"]) else ""
        rows.extend([coef_row, se_row])

    observations = {"Term": "Observations"}
    fit = {"Term": "R-squared / pseudo R-squared"}
    for model in models:
        model_rows = group[group["model"].astype(str) == model]
        observations[model] = str(int(model_rows["observations"].dropna().iloc[0]))
        fit_value = model_rows["fit_stat"].dropna()
        fit[model] = _fmt_number(fit_value.iloc[0]) if not fit_value.empty else ""
    rows.extend([observations, fit])
    return pd.DataFrame(rows)


def _format_summary_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["value"] = df.apply(lambda row: f"{row['mean']:.3f} ({row['std_dev']:.3f})", axis=1)
    table = df.pivot_table(
        index="variable",
        columns="treatment",
        values="value",
        aggfunc="first",
        sort=False,
    ).fillna("")
    observations = df.groupby("treatment", sort=False)["observations"].first()
    table.loc["N"] = observations.astype(str)
    return table.reset_index().rename(columns={"variable": "Variable"})


def _write_table_pair(table: pd.DataFrame, folder: Path, name: str) -> dict[str, str]:
    folder.mkdir(parents=True, exist_ok=True)
    csv_path = folder / f"{name}.csv"
    tex_path = folder / f"{name}.tex"
    table.to_csv(csv_path, index=False)
    _write_latex(table, tex_path)
    return {"csv": str(csv_path), "tex": str(tex_path)}


def build() -> dict[str, dict[str, str]]:
    PAPER_TABLES.mkdir(parents=True, exist_ok=True)
    APPENDIX_TABLES.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, dict[str, str]] = {}

    summary_path = TABLES / "appendix_table_a1_summary_statistics.csv"
    if summary_path.exists():
        artifacts["Table A.1"] = _write_table_pair(
            _format_summary_table(summary_path),
            APPENDIX_TABLES,
            TABLE_NAMES["Table A.1"],
        )

    for source in [TABLES / "main_tables_results.csv", TABLES / "appendix_tables_results.csv"]:
        if not source.exists():
            continue
        df = pd.read_csv(source)
        df = _add_p_values(df)
        df.to_csv(source, index=False)
        for table_id, group in df.groupby("table_id", sort=False):
            folder = PAPER_TABLES if table_id in {"Table 2", "Table 3", "Table 4"} else APPENDIX_TABLES
            artifacts[str(table_id)] = _write_table_pair(
                _formatted_regression_table(group),
                folder,
                TABLE_NAMES[str(table_id)],
            )

    return artifacts


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
