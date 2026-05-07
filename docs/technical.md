# Technical Notes

## Entry Points

The researcher-facing walkthrough is `analysis.ipynb`.

The scripted entrypoint is:

```bash
uv run python run_analysis.py
```

`replicate.py` and `main.py` are compatibility wrappers around `run_analysis.py`.

## Script Pipeline

`run_analysis.py` runs these steps:

1. Assemble raw treatment CSV files into derived analysis datasets.
2. Regenerate paper and appendix figures.
3. Regenerate Stata regression table data.
4. Format table outputs as readable CSV files and LaTeX table fragments.

The setup-only command is:

```bash
uv run python run_analysis.py --check-setup
```

It reports Python, package, OS, and Stata availability without rebuilding outputs.

## Data Inputs

The public analysis pipeline uses:

- `data/raw/ge_prosocial/combined.csv`
- `data/raw/neutral/combined.csv`
- `data/raw/efficiency/combined.csv`

The derived datasets in `data/derived/` are generated from these inputs.

## Stata

Stata is resolved in this order:

1. `STATA_PATH` environment variable.
2. Stata executables on `PATH`.
3. Common Stata installation paths on macOS, Windows, and Linux.

Stata 17 or newer is required. The script pipeline runs Stata do-files through the Stata executable. The notebook configures `pystata` from the same resolver and then runs the same Stata do-files from Python.

## Outputs

The main outputs are in `results/paper` and `results/appendix`.

Internal machine-readable files and Stata logs are written to `results/_intermediate/` while the analysis runs. That folder is ignored by git because the researcher-facing table and figure files are already written to `results/paper` and `results/appendix`.
