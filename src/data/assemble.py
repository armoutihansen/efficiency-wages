from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning

from src.paths import DATA_DERIVED, RAW_COMBINED, TREATMENT_LABELS, WAGES


ULTIMATUM_ACCEPT_PREFIX = "Ultimatum_Accept_Agent_atShare_Principal_"


def _load_raw() -> dict[str, pd.DataFrame]:
    frames = {
        name: pd.read_csv(path)
        for name, path in RAW_COMBINED.items()
        if path.exists()
    }
    frames["neutral"]["Treatment"] = "N"
    frames["efficiency"]["Treatment"] = "PAN"
    return frames


def _minimum_ug_offer(row: pd.Series) -> int:
    for principal_share, minimum_agent_share in [
        (90, 10),
        (80, 20),
        (70, 30),
        (60, 40),
        (50, 50),
        (40, 60),
        (30, 70),
        (20, 80),
        (10, 90),
    ]:
        if row.get(f"{ULTIMATUM_ACCEPT_PREFIX}{principal_share}", 0) == 1:
            return minimum_agent_share
    return 100


def _charitable_giving_for_neutral(row: pd.Series) -> float:
    if row["Agent"] == 1:
        self_cols = ["P1Self1", "P1Self2", "P1Self3", "P1Self4", "P1Self5"]
        return 100 - row[self_cols].mean()
    return 100 - row["P1SelfP"]


def _standardize_frame(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    frame = frame.copy()
    frame["source_treatment"] = label
    frame["Agent"] = (frame["Type"] == 2).astype(int)
    frame["treatment_label"] = frame["Treatment"].map(TREATMENT_LABELS)

    if label == "neutral":
        frame["giveC"] = frame.apply(_charitable_giving_for_neutral, axis=1)
    else:
        frame["giveC"] = frame["DictatorCharity"]

    agents = frame["Agent"] == 1
    frame.loc[agents, "min_ug"] = frame.loc[agents].apply(_minimum_ug_offer, axis=1)
    return frame


def _make_agent_long(df: pd.DataFrame) -> pd.DataFrame:
    agent = df[df["Agent"] == 1].copy().reset_index(drop=True)
    agent["n"] = np.arange(len(agent))
    rows: list[pd.DataFrame] = []
    base_cols = [
        "n",
        "Treatment",
        "treatment_label",
        "gender",
        "age",
        "study",
        "DictatorCharity",
        "giveC",
        "min_ug",
        "Favor_intentions",
        "Favor_revenge",
        "Favor_return",
        "Punish_Self",
        "Punish_Others",
        "Gift",
        "Give_Charity",
        "Donation_Good_Cause",
    ]
    for wage in WAGES:
        rows.append(
            pd.DataFrame(
                {
                    **{col: agent[col].to_numpy() for col in base_cols if col in agent.columns},
                    "Wage": wage,
                    "Effort": agent[f"PA_OfferedEffort_Agent_atWage_{wage}"].fillna(0).to_numpy(),
                    "Acceptance": agent[f"PA_Accept_Agent_atWage_{wage}"].fillna(0).to_numpy(),
                }
            )
        )
    return pd.concat(rows, ignore_index=True).sort_values(["n", "Wage"])


def _make_principal_long(df: pd.DataFrame) -> pd.DataFrame:
    principals = df[df["Agent"] == 0].copy().reset_index(drop=True)
    principals["principal_n"] = np.arange(len(principals))
    rows: list[pd.DataFrame] = []
    base_cols = [
        "principal_n",
        "Treatment",
        "treatment_label",
        "PA_Offer_Principal",
        "PAWage",
        "OptimalWage",
        "real_profitmax_wage",
        "DictatorCharity",
        "giveC",
        "gender",
        "age",
        "study",
    ]
    for wage in WAGES:
        rows.append(
            pd.DataFrame(
                {
                    **{
                        col: principals[col].to_numpy()
                        for col in base_cols
                        if col in principals.columns
                    },
                    "Wage": wage,
                    "ExpectedAcceptance": principals[
                        f"PA_ExpectedAcceptance_Principal_atWage_{wage}"
                    ]
                    .fillna(0)
                    .to_numpy(),
                    "ExpectedEffort": principals[f"PA_ExpectedEffort_Principal_atWage_{wage}"]
                    .fillna(0)
                    .to_numpy(),
                }
            )
        )
    return pd.concat(rows, ignore_index=True).sort_values(["principal_n", "Wage"])


def build() -> dict[str, object]:
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    raw = {key: _standardize_frame(value, key) for key, value in _load_raw().items()}

    df = pd.concat(
        [raw["ge_prosocial"], raw["neutral"], raw["efficiency"]],
        ignore_index=True,
        sort=False,
    )
    agent_long = _make_agent_long(df)
    principal_long = _make_principal_long(df)
    principals = df[df["Agent"] == 0].copy().reset_index(drop=True)
    principals["principal_n"] = np.arange(len(principals))

    df.to_csv(DATA_DERIVED / "analysis_sample.csv", index=False)
    agent_long.to_csv(DATA_DERIVED / "agent_wage_long.csv", index=False)
    principal_long.to_csv(DATA_DERIVED / "principal_beliefs_long.csv", index=False)
    principals.to_csv(DATA_DERIVED / "principals.csv", index=False)

    counts = {
        treatment: {
            "observations": int(group.shape[0]),
            "agents": int((group["Agent"] == 1).sum()),
            "principals": int((group["Agent"] == 0).sum()),
        }
        for treatment, group in df.groupby("Treatment")
    }
    (DATA_DERIVED / "sample_counts.json").write_text(json.dumps(counts, indent=2) + "\n")
    return counts


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
