from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
PAPER_TABLES = RESULTS / "paper" / "tables"
PAPER_FIGURES = RESULTS / "paper" / "figures"
APPENDIX_TABLES = RESULTS / "appendix" / "tables"
APPENDIX_FIGURES = RESULTS / "appendix" / "figures"
INTERMEDIATE = RESULTS / "_intermediate"
LOGS = INTERMEDIATE / "logs"

# Internal machine-readable files used while generating the researcher-facing
# tables and figures. This folder is ignored by git.
OUTPUTS = INTERMEDIATE
TABLES = INTERMEDIATE / "tables"
FIGURES = INTERMEDIATE / "figures"

WAGES = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 75, 85, 95]

TREATMENT_LABELS = {
    "P": "GE",
    "S": "Prosocial",
    "N": "Neutral",
    "PAN": "Efficiency",
}

RAW_COMBINED = {
    "ge_prosocial": DATA_RAW / "ge_prosocial" / "combined.csv",
    "neutral": DATA_RAW / "neutral" / "combined.csv",
    "efficiency": DATA_RAW / "efficiency" / "combined.csv",
}
