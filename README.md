# Efficiency Wages with Motivated Agents

This repository contains the data and code needed to run the analysis for **"Efficiency Wages with Motivated Agents"** and its online appendix.

Publication: https://www.sciencedirect.com/science/article/pii/S0899825624000307?via%3Dihub

The published paper and online appendix are not included in this repository. The publication link above is the source of truth for the article and supplement.

## Requirements

- `uv`: https://docs.astral.sh/uv/
- Stata 17 or newer for the regression tables.

Python is managed by `uv`; you do not need to create a Python environment manually.

## Run The Analysis

For a readable walkthrough, open `analysis.ipynb`. The notebook starts from the raw treatment CSV files, assembles the analysis data, runs the paper and appendix table code, and displays the figures and tables in the order they appear in the paper and online appendix.

To run the complete scripted analysis from the repository root:

```bash
uv run python run_analysis.py
```

The generated outputs are written to:

- `results/paper/`: main paper Tables 2-4 and Figures 2-4.
- `results/appendix/`: online appendix Tables A.1-A.9 and Figures A.1-A.8.

Tables are generated as `.tex` fragments and readable `.csv` files. Figures are generated as `.png` files.

## Stata Setup

The analysis runner looks for Stata on macOS, Windows, and Linux. If Stata is not found automatically, set `STATA_PATH` to the full executable path.

macOS example:

```bash
STATA_PATH="/Applications/Stata/StataSE.app/Contents/MacOS/stata-se" uv run python run_analysis.py
```

Windows PowerShell example:

```powershell
$env:STATA_PATH="C:\Program Files\Stata19\StataSE-64.exe"
uv run python run_analysis.py
```

To check Python packages and Stata availability without running the analysis:

```bash
uv run python run_analysis.py --check-setup
```

## Notebook

To execute the notebook locally:

```bash
uv run jupyter notebook analysis.ipynb
```

The notebook uses `pystata` for the Stata sections. It uses the same Stata resolver as the script workflow, so `STATA_PATH` can be used when Stata is not found automatically.

## Repository Layout

- `analysis.ipynb`: researcher-facing walkthrough of the paper and appendix analysis.
- `data/raw/`: treatment-level CSV inputs.
- `data/derived/`: intermediate datasets generated from the raw inputs.
- `src/data/`: data assembly code.
- `src/analysis/`: figure, table, and formatting code.
- `results/`: generated paper and appendix outputs.

More implementation details are in `docs/technical.md`.
