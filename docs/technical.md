# Technical Notes

## Entry Points

The notebook entrypoint is:

```bash
uv run jupyter notebook analysis.ipynb
```

The scripted entrypoint is:

```bash
uv run python run_analysis.py
```

Both workflows start from the raw CSV inputs and write final artifacts to `results/paper` and `results/appendix`.

## Notebook Workflow

`analysis.ipynb` is a self-contained walkthrough for researchers who prefer to inspect and run the analysis step by step. It derives the analysis datasets directly in notebook cells, generates the Python figures directly in notebook cells, and runs the Stata regression commands through inline `pystata` cells.

The notebook intentionally does not call `run_analysis.py`, import `src.data.assemble`, import `src.analysis.*`, or call external Stata do-files.

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

The derived datasets in `data/derived/` are generated from these inputs at runtime. They are ignored by git because they can be rebuilt.

## Stata

Stata is resolved in this order:

1. `STATA_PATH` environment variable.
2. Stata executables on `PATH`.
3. Common Stata installation paths on macOS, Windows, and Linux.

Stata 17 or newer is required. The script pipeline runs Stata do-files through the Stata executable. The notebook configures `pystata` directly and runs inline Stata commands from Python.

## Outputs

The main outputs are in `results/paper` and `results/appendix`.

Internal machine-readable files and Stata logs are written to `results/_intermediate/` while the analysis runs. That folder is ignored by git because the researcher-facing table and figure files are already written to `results/paper` and `results/appendix`.
