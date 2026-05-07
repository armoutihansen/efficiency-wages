from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.paths import (
    APPENDIX_FIGURES,
    DATA_DERIVED,
    FIGURES,
    PAPER_FIGURES,
    TABLES,
    WAGES,
)


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
    profits = [
        100 if pd.isna(effort) else multiplier * effort - wage + 100
        for effort, wage in zip(efforts, WAGES)
    ]
    return WAGES[int(np.nanargmax(profits))]


def _belief_profit_max_wage(row: pd.Series) -> int:
    efforts = [row[f"wage_{wage}"] for wage in WAGES]
    return _profit_max_wage(efforts, row["Treatment"])


def _agent_profit_max_wages(df: pd.DataFrame) -> pd.DataFrame:
    agents = df[df["Agent"] == 1].copy().reset_index(drop=True)
    agents["real_profitmax_wage"] = agents.apply(
        lambda row: _profit_max_wage(
            [row[f"PA_OfferedEffort_Agent_atWage_{wage}"] for wage in WAGES],
            row["Treatment"],
        ),
        axis=1,
    )
    return agents[["Treatment", "real_profitmax_wage"]]


def _principal_wage_summary(df: pd.DataFrame, principal_long: pd.DataFrame) -> pd.DataFrame:
    principals = df[df["Agent"] == 0].copy().reset_index(drop=True)
    principals["principal_n"] = np.arange(len(principals))

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

    agent_profitmax = _agent_profit_max_wages(df)
    pieces = []
    for treatment in PROFIT_MULTIPLIER:
        principal_group = merged[merged["Treatment"] == treatment].copy().reset_index(drop=True)
        agent_group = agent_profitmax[agent_profitmax["Treatment"] == treatment].reset_index(drop=True)
        if len(principal_group) != len(agent_group):
            raise ValueError(
                f"Cannot align principal and agent profit-maximizing wages for {treatment}: "
                f"{len(principal_group)} principals and {len(agent_group)} agents."
            )
        principal_group["real_profitmax_wage"] = agent_group["real_profitmax_wage"]
        pieces.append(principal_group)
    merged = pd.concat(pieces, ignore_index=True)
    merged["Treatment label"] = merged["Treatment"].map(
        {"P": "GE", "S": "Prosocial", "N": "Neutral", "PAN": "Efficiency"}
    )

    merged[
        [
            "Treatment label",
            "PAWage",
            "OptimalWage",
            "expected_profitmax_wage",
            "real_profitmax_wage",
        ]
    ].to_csv(TABLES / "wage_summary_by_principal.csv", index=False)

    rows = []
    for source_col, wage_type in [
        ("PAWage", "Offered"),
        ("OptimalWage", "Guessed Profit Maximizing"),
        ("expected_profitmax_wage", "Expected Profit Maximizing"),
        ("real_profitmax_wage", "Real Profit Maximizing"),
    ]:
        rows.append(
            merged[["Treatment label", source_col]]
            .rename(columns={"Treatment label": "Treatment", source_col: "Wage"})
            .assign(**{"Wage type": wage_type})
        )
    summary = pd.concat(rows, ignore_index=True)
    summary.to_csv(TABLES / "wage_summary.csv", index=False)
    return summary


def _plot_wage_comparison(data: pd.DataFrame, order: list[str]) -> None:
    sns.barplot(
        data=data,
        x="Treatment",
        y="Wage",
        hue="Wage type",
        estimator=np.mean,
        errorbar=("ci", 95),
        capsize=0.05,
        err_kws={"linewidth": 1},
        linewidth=1,
        edgecolor="black",
        order=order,
        hue_order=[
            "Offered",
            "Expected Profit Maximizing",
            "Guessed Profit Maximizing",
            "Real Profit Maximizing",
        ],
    )
    plt.ylabel("Wage")


def _savefig(folder: Path, path: str) -> None:
    plt.tight_layout()
    plt.savefig(folder / path, dpi=300)
    plt.close()


def build() -> dict[str, str]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    APPENDIX_FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="ticks", context="paper", font_scale=1.25)

    df, agent_long, principal_long = _load()
    wage_summary = _principal_wage_summary(df, principal_long)

    main = agent_long[agent_long["Treatment"].isin(["P", "S"])].copy()
    main["Treatment"] = main["treatment_label"]
    sns.lineplot(data=main, x="Wage", y="Effort", hue="Treatment", marker="o", errorbar=("ci", 95))
    plt.ylabel("Mean chosen effort")
    _savefig(PAPER_FIGURES, "main_fig_2_chosen_effort.png")

    main_wages = wage_summary[wage_summary["Treatment"].isin(["GE", "Prosocial"])]
    _plot_wage_comparison(main_wages, ["GE", "Prosocial"])
    plt.xticks(rotation=0)
    _savefig(PAPER_FIGURES, "main_fig_3_wage_comparisons.png")

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
    g.savefig(PAPER_FIGURES / "main_fig_4_chosen_expected_effort.png", dpi=300)
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
    _savefig(APPENDIX_FIGURES, "supp_fig_a1_acceptance_wage.png")

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
    _savefig(APPENDIX_FIGURES, "supp_fig_a2_chosen_effort_all.png")

    _plot_wage_comparison(wage_summary, DISPLAY_ORDER)
    _savefig(APPENDIX_FIGURES, "supp_fig_a3_wage_comparisons_all.png")

    fig_a4 = pd.read_csv(TABLES / "wage_summary_by_principal.csv")
    fig_a4 = fig_a4[fig_a4["Treatment label"].isin(["GE", "Prosocial"])].copy()
    medians_beliefs = fig_a4.groupby("Treatment label")["expected_profitmax_wage"].transform("median")
    fig_a4["Beliefs"] = np.where(fig_a4["expected_profitmax_wage"] <= medians_beliefs, "Low", "High")
    sns.barplot(
        data=fig_a4,
        x="Treatment label",
        y="PAWage",
        hue="Beliefs",
        estimator=np.mean,
        errorbar=("ci", 95),
        capsize=0.05,
        err_kws={"linewidth": 1},
        linewidth=1,
        edgecolor="black",
        order=["GE", "Prosocial"],
        hue_order=["Low", "High"],
    )
    plt.xlabel("Treatment")
    plt.ylabel("Wage")
    _savefig(APPENDIX_FIGURES, "supp_fig_a4_beliefs_based_profitmax_wage.png")

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
        g.savefig(APPENDIX_FIGURES / filename, dpi=220)
        plt.close("all")

    artifacts = {
        path.name: str(path)
        for path in [*sorted(PAPER_FIGURES.glob("*.png")), *sorted(APPENDIX_FIGURES.glob("*.png"))]
    }
    (FIGURES / "manifest.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    return artifacts


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
