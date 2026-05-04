from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.replication_paths import DATA_DERIVED, FIGURES, TABLES, WAGES


PROFIT_MULTIPLIER = {"P": 10, "S": 10, "N": 10, "PAN": 35}
DISPLAY_ORDER = ["GE", "Prosocial", "Neutral", "Efficiency"]


def _load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(DATA_DERIVED / "analysis_sample.csv"),
        pd.read_csv(DATA_DERIVED / "agent_wage_long.csv"),
        pd.read_csv(DATA_DERIVED / "principal_beliefs_long.csv"),
    )


def _profit_max_wage(efforts: list[float], treatment: str) -> int:
    multiplier = PROFIT_MULTIPLIER[treatment]
    profits = [multiplier * effort - wage for effort, wage in zip(efforts, WAGES)]
    return WAGES[int(np.nanargmax(profits))]


def _mean_real_profit_max_wages(agent_long: pd.DataFrame) -> dict[str, int]:
    results: dict[str, int] = {}
    for treatment, group in agent_long.groupby("Treatment"):
        means = [group.loc[group["Wage"] == wage, "Effort"].mean() for wage in WAGES]
        results[treatment] = _profit_max_wage(means, treatment)
    return results


def _belief_profit_max_wage(row: pd.Series) -> int:
    efforts = [row[f"wage_{wage}"] for wage in WAGES]
    return _profit_max_wage(efforts, row["Treatment"])


def _principal_wage_summary(
    df: pd.DataFrame, principal_long: pd.DataFrame, agent_long: pd.DataFrame
) -> pd.DataFrame:
    principals = df[df["Agent"] == 0].copy().reset_index(drop=True)
    principals["principal_n"] = np.arange(len(principals))
    real_pmw = _mean_real_profit_max_wages(agent_long)

    expected = principal_long.pivot_table(
        index=["principal_n", "Treatment"], columns="Wage", values="ExpectedEffort"
    ).reset_index()
    expected.columns = [
        f"wage_{int(col)}" if isinstance(col, (int, float)) else col for col in expected.columns
    ]
    expected["expected_profitmax_wage"] = expected.apply(_belief_profit_max_wage, axis=1)

    merged = principals.merge(
        expected[["principal_n", "expected_profitmax_wage"]],
        on="principal_n",
        how="left",
    )
    rows = []
    for treatment, label in [
        ("P", "GE"),
        ("S", "Prosocial"),
        ("N", "Neutral"),
        ("PAN", "Efficiency"),
    ]:
        group = merged[merged["Treatment"] == treatment]
        rows.extend(
            [
                {
                    "Treatment": label,
                    "Wage type": "Offered",
                    "Wage": group["PA_Offer_Principal"].mean(),
                },
                {
                    "Treatment": label,
                    "Wage type": "Expected profit-maximizing",
                    "Wage": group["expected_profitmax_wage"].mean(),
                },
                {
                    "Treatment": label,
                    "Wage type": "Guessed profit-maximizing",
                    "Wage": group["OptimalWage"].mean(),
                },
                {
                    "Treatment": label,
                    "Wage type": "Average real profit-maximizing",
                    "Wage": real_pmw[treatment],
                },
            ]
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(TABLES / "wage_summary.csv", index=False)
    return summary


def _savefig(path: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / path, dpi=300)
    plt.close()


def build() -> dict[str, str]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="ticks", context="paper", font_scale=1.25)

    df, agent_long, principal_long = _load()
    wage_summary = _principal_wage_summary(df, principal_long, agent_long)

    main = agent_long[agent_long["Treatment"].isin(["P", "S"])].copy()
    main["Treatment"] = main["treatment_label"]
    sns.lineplot(data=main, x="Wage", y="Effort", hue="Treatment", marker="o", errorbar=("ci", 95))
    plt.ylabel("Mean chosen effort")
    _savefig("main_fig_2_chosen_effort.png")

    main_wages = wage_summary[wage_summary["Treatment"].isin(["GE", "Prosocial"])]
    sns.barplot(
        data=main_wages,
        x="Treatment",
        y="Wage",
        hue="Wage type",
        errorbar=None,
        edgecolor="black",
    )
    plt.ylabel("Wage")
    plt.xticks(rotation=0)
    _savefig("main_fig_3_wage_comparisons.png")

    chosen = agent_long[agent_long["Treatment"].isin(["P", "S"])][
        ["Treatment", "treatment_label", "Wage", "Effort"]
    ].copy()
    chosen["Effort type"] = "Chosen effort"
    expected = principal_long[principal_long["Treatment"].isin(["P", "S"])][
        ["Treatment", "treatment_label", "Wage", "ExpectedEffort"]
    ].rename(columns={"ExpectedEffort": "Effort"})
    expected["Effort type"] = "Expected effort"
    beliefs = pd.concat([chosen, expected], ignore_index=True)
    g = sns.relplot(
        data=beliefs,
        x="Wage",
        y="Effort",
        hue="Effort type",
        col="treatment_label",
        kind="line",
        marker="o",
        errorbar=("ci", 95),
        height=4,
        aspect=1.25,
    )
    g.set_axis_labels("Wage", "Mean effort")
    g.set_titles("{col_name}")
    g.savefig(FIGURES / "main_fig_4_chosen_expected_effort.png", dpi=300)
    plt.close("all")

    acceptance = agent_long[agent_long["Treatment"].isin(["P", "S"])].copy()
    acceptance["Treatment"] = acceptance["treatment_label"]
    sns.lineplot(
        data=acceptance,
        x="Wage",
        y="Acceptance",
        hue="Treatment",
        marker="o",
        errorbar=("ci", 95),
    )
    plt.ylabel("Acceptance share")
    _savefig("supp_fig_a1_acceptance_wage.png")

    all_effort = agent_long.copy()
    all_effort["Treatment"] = pd.Categorical(
        all_effort["treatment_label"], categories=DISPLAY_ORDER, ordered=True
    )
    sns.lineplot(
        data=all_effort,
        x="Wage",
        y="Effort",
        hue="Treatment",
        marker="o",
        errorbar=("ci", 95),
    )
    plt.ylabel("Mean chosen effort")
    _savefig("supp_fig_a2_chosen_effort_all.png")

    sns.barplot(
        data=wage_summary,
        x="Treatment",
        y="Wage",
        hue="Wage type",
        order=DISPLAY_ORDER,
        errorbar=None,
        edgecolor="black",
    )
    plt.ylabel("Wage")
    plt.xticks(rotation=15)
    _savefig("supp_fig_a3_wage_comparisons_all.png")

    median_expected = wage_summary[
        (wage_summary["Treatment"].isin(["GE", "Prosocial"]))
        & (wage_summary["Wage type"] == "Expected profit-maximizing")
    ].copy()
    offered = wage_summary[
        (wage_summary["Treatment"].isin(["GE", "Prosocial"]))
        & (wage_summary["Wage type"] == "Offered")
    ].copy()
    median_expected["Wage type"] = "Beliefs-based profit-maximizing"
    fig_a4 = pd.concat([offered, median_expected], ignore_index=True)
    sns.barplot(
        data=fig_a4,
        x="Treatment",
        y="Wage",
        hue="Wage type",
        errorbar=None,
        edgecolor="black",
    )
    plt.ylabel("Wage")
    _savefig("supp_fig_a4_beliefs_based_profitmax_wage.png")

    for treatment, filename in [
        ("P", "supp_fig_a5_individual_effort_ge.png"),
        ("S", "supp_fig_a6_individual_effort_prosocial.png"),
        ("N", "supp_fig_a7_individual_effort_neutral.png"),
        ("PAN", "supp_fig_a8_individual_effort_efficiency.png"),
    ]:
        subset = agent_long[agent_long["Treatment"] == treatment].copy()
        g = sns.relplot(
            data=subset,
            x="Wage",
            y="Effort",
            col="n",
            col_wrap=6,
            kind="line",
            marker="o",
            height=1.6,
            aspect=1.1,
            errorbar=None,
        )
        g.set(xticks=[1, 25, 50, 75, 95], yticks=[0, 5, 10], ylim=(-0.3, 10.3))
        g.set_axis_labels("Wage", "Effort")
        g.savefig(FIGURES / filename, dpi=220)
        plt.close("all")

    artifacts = {path.name: str(path) for path in sorted(FIGURES.glob("*.png"))}
    (FIGURES / "manifest.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    return artifacts


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
