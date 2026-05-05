from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.replication_paths import DATA_DERIVED, FIGURES, OUTPUTS, TABLES, WAGES
from src.stata import resolve_stata


EXPECTED_COUNTS = {
    "P": {"observations": 94, "agents": 47, "principals": 47},
    "S": {"observations": 96, "agents": 48, "principals": 48},
    "N": {"observations": 90, "agents": 45, "principals": 45},
    "PAN": {"observations": 120, "agents": 60, "principals": 60},
}

EXPECTED_FIGURES = [
    "main_fig_2_chosen_effort.png",
    "main_fig_3_wage_comparisons.png",
    "main_fig_4_chosen_expected_effort.png",
    "supp_fig_a1_acceptance_wage.png",
    "supp_fig_a2_chosen_effort_all.png",
    "supp_fig_a3_wage_comparisons_all.png",
    "supp_fig_a4_beliefs_based_profitmax_wage.png",
    "supp_fig_a5_individual_effort_ge.png",
    "supp_fig_a6_individual_effort_prosocial.png",
    "supp_fig_a7_individual_effort_neutral.png",
    "supp_fig_a8_individual_effort_efficiency.png",
]


def _close(actual: float, expected: float, tolerance: float = 0.01) -> bool:
    return bool(abs(actual - expected) <= tolerance)


def _profit_max_wage(efforts: list[float], multiplier: int) -> int:
    profits = [multiplier * effort - wage for effort, wage in zip(efforts, WAGES)]
    return WAGES[int(np.nanargmax(profits))]


def run_checks(require_stata: bool = True, require_stata_tables: bool = True) -> dict[str, object]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_DERIVED / "analysis_sample.csv")
    agent_long = pd.read_csv(DATA_DERIVED / "agent_wage_long.csv")
    table_results = (
        pd.read_csv(TABLES / "main_tables_results.csv")
        if (TABLES / "main_tables_results.csv").exists()
        else pd.DataFrame()
    )
    appendix_results = (
        pd.read_csv(TABLES / "appendix_tables_results.csv")
        if (TABLES / "appendix_tables_results.csv").exists()
        else pd.DataFrame()
    )
    appendix_summary = (
        pd.read_csv(TABLES / "appendix_table_a1_summary_statistics.csv")
        if (TABLES / "appendix_table_a1_summary_statistics.csv").exists()
        else pd.DataFrame()
    )

    checks: list[dict[str, object]] = []

    for treatment, expected in EXPECTED_COUNTS.items():
        group = df[df["Treatment"] == treatment]
        actual = {
            "observations": int(group.shape[0]),
            "agents": int((group["Agent"] == 1).sum()),
            "principals": int((group["Agent"] == 0).sum()),
        }
        checks.append(
            {
                "check": f"sample_count_{treatment}",
                "pass": actual == expected,
                "actual": actual,
                "expected": expected,
            }
        )

    principals = df[df["Agent"] == 0]
    wage_means = principals.groupby("Treatment")["PA_Offer_Principal"].mean()
    checks.extend(
        [
            {
                "check": "offered_wage_mean_ge",
                "pass": _close(wage_means["P"], 25.574, 0.01),
                "actual": float(wage_means["P"]),
                "expected": 25.574,
            },
            {
                "check": "offered_wage_mean_prosocial",
                "pass": _close(wage_means["S"], 35.771, 0.01),
                "actual": float(wage_means["S"]),
                "expected": 35.771,
            },
            {
                "check": "wage_offer_regression_treatment_coefficient",
                "pass": _close(wage_means["S"] - wage_means["P"], 10.196, 0.01),
                "actual": float(wage_means["S"] - wage_means["P"]),
                "expected": 10.196,
            },
        ]
    )

    for treatment, expected, multiplier in [("P", 45, 10), ("S", 40, 10)]:
        group = agent_long[agent_long["Treatment"] == treatment]
        efforts = [group.loc[group["Wage"] == wage, "Effort"].mean() for wage in WAGES]
        actual = _profit_max_wage(efforts, multiplier)
        checks.append(
            {
                "check": f"average_real_profitmax_wage_{treatment}",
                "pass": actual == expected,
                "actual": actual,
                "expected": expected,
            }
        )

    if not table_results.empty:
        coef = table_results[
            (table_results["table_id"] == "Table 4")
            & (table_results["model"] == 1)
            & (table_results["term"] == "Prosocial treatment")
        ]["coefficient"].iloc[0]
        checks.append(
            {
                "check": "stata_table4_model1_treatment_coefficient",
                "pass": _close(float(coef), 10.196, 0.01),
                "actual": float(coef),
                "expected": 10.196,
            }
        )
    else:
        checks.append(
            {
                "check": "stata_main_tables_results_exist",
                "pass": not require_stata_tables,
                "skipped": not require_stata_tables,
                "actual": "missing",
                "expected": str(TABLES / "main_tables_results.csv"),
            }
        )

    if not appendix_summary.empty:
        appendix_summary_checks = [
            ("appendix_table_a1_ge_age_mean", "GE", "Age", "mean", 24.361702, 0.001),
            ("appendix_table_a1_prosocial_male_mean", "Prosocial", "Male", "mean", 0.677083, 0.001),
            ("appendix_table_a1_efficiency_age_sd", "Efficiency", "Age", "std_dev", 6.627499, 0.001),
            ("appendix_table_a1_neutral_observations", "Neutral", "Age", "observations", 90, 0),
        ]
        for check_name, treatment, variable, column, expected, tolerance in appendix_summary_checks:
            actual = appendix_summary[
                (appendix_summary["treatment"] == treatment)
                & (appendix_summary["variable"] == variable)
            ][column].iloc[0]
            checks.append(
                {
                    "check": check_name,
                    "pass": _close(float(actual), float(expected), tolerance),
                    "actual": float(actual),
                    "expected": expected,
                }
            )
    else:
        checks.append(
            {
                "check": "appendix_table_a1_summary_statistics_exist",
                "pass": False,
                "actual": "missing",
                "expected": str(TABLES / "appendix_table_a1_summary_statistics.csv"),
            }
        )

    if not appendix_results.empty:
        expected_table_ids = {f"Table A.{number}" for number in range(2, 10)}
        actual_table_ids = set(appendix_results["table_id"])
        checks.append(
            {
                "check": "appendix_regression_table_ids_present",
                "pass": expected_table_ids.issubset(actual_table_ids),
                "actual": sorted(actual_table_ids),
                "expected": sorted(expected_table_ids),
            }
        )

        appendix_numeric_checks = [
            ("appendix_table_a2_ge_real_wage", "Table A.2", "GE real", "Wage", 0.09064, 0.001),
            ("appendix_table_a3_efficiency_expected_wage", "Table A.3", "Efficiency expected", "Wage", 0.05864, 0.001),
            ("appendix_table_a4_model1_wage_below_5", "Table A.4", "1", "Wage<5", -0.71721, 0.001),
            ("appendix_table_a5_model2_efficiency", "Table A.5", "2", "Efficiency treatment", -0.11005, 0.001),
            ("appendix_table_a6_model1_wage", "Table A.6", "1", "Wage", 0.08557, 0.001),
            ("appendix_table_a7_model2_efficiency", "Table A.7", "2", "Efficiency treatment", -1.08512, 0.001),
            ("appendix_table_a8_model1_ge", "Table A.8", "1", "GE treatment", -10.19637, 0.001),
            ("appendix_table_a9_model1_efficiency", "Table A.9", "1", "Efficiency treatment", 10.91277, 0.001),
        ]
        for check_name, table_id, model, term, expected, tolerance in appendix_numeric_checks:
            match = appendix_results[
                (appendix_results["table_id"] == table_id)
                & (appendix_results["model"].astype(str) == model)
                & (appendix_results["term"] == term)
            ]
            actual = float(match["coefficient"].iloc[0]) if not match.empty else np.nan
            checks.append(
                {
                    "check": check_name,
                    "pass": _close(actual, expected, tolerance),
                    "actual": actual,
                    "expected": expected,
                }
            )
    else:
        checks.append(
            {
                "check": "appendix_regression_tables_exist",
                "pass": not require_stata_tables,
                "skipped": not require_stata_tables,
                "actual": "missing",
                "expected": str(TABLES / "appendix_tables_results.csv"),
            }
        )

    for figure in EXPECTED_FIGURES:
        path = FIGURES / figure
        checks.append(
            {
                "check": f"artifact_{figure}",
                "pass": path.exists() and path.stat().st_size > 0,
                "actual": path.stat().st_size if path.exists() else 0,
                "expected": ">0 bytes",
            }
        )

    stata = resolve_stata()
    checks.append(
        {
            "check": "stata_cli_available",
            "pass": stata.usable if require_stata else True,
            "skipped": not require_stata,
            "actual": stata.to_dict(),
            "expected": "Stata 17 or newer",
        }
    )

    passed = bool(all(bool(check["pass"]) for check in checks))
    result = {"pass": passed, "checks": checks, "stata": stata.to_dict()}
    (OUTPUTS / "verification_report.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    report = run_checks()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["pass"] else 1)
