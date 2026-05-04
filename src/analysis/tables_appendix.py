from __future__ import annotations

import json

import pandas as pd

from src.replication_paths import DATA_DERIVED, TABLES


TREATMENT_ORDER = ["P", "S", "N", "PAN"]
TREATMENT_NAMES = {
    "P": "GE",
    "S": "Prosocial",
    "N": "Neutral",
    "PAN": "Efficiency",
}


def build_summary_statistics() -> dict[str, str]:
    TABLES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_DERIVED / "analysis_sample.csv")

    rows: list[dict[str, object]] = []
    for treatment in TREATMENT_ORDER:
        group = df[df["Treatment"] == treatment]
        variables = {
            "Age": group["age"],
            "Male": group["gender"],
            "Study subject #1": (group["study"] == 1).astype(int),
            "Study subject #2": (group["study"] == 2).astype(int),
            "Study subject #3": (group["study"] == 3).astype(int),
        }
        for variable, values in variables.items():
            rows.append(
                {
                    "table_id": "Table A.1",
                    "treatment": TREATMENT_NAMES[treatment],
                    "variable": variable,
                    "mean": values.mean(),
                    "std_dev": values.std(ddof=1),
                    "observations": int(values.count()),
                }
            )

    output = TABLES / "appendix_table_a1_summary_statistics.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    return {"summary_statistics": str(output)}


def build() -> dict[str, str]:
    return build_summary_statistics()


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
