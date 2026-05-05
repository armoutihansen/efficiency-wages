# Technical Notes

## Pipeline

The primary entrypoint is:

```bash
uv run python run_analysis.py
```

It runs these steps:

1. Collect setup information for Python, dependencies, OS, and Stata.
2. Assemble raw treatment CSV files into derived analysis datasets.
3. Regenerate paper and appendix figures.
4. Regenerate Stata regression table data.
5. Format table outputs as readable CSV files and LaTeX table fragments.
6. Write secondary diagnostics.

`replicate.py` and `main.py` are compatibility wrappers around `run_analysis.py`.

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

Stata 17 or newer is required. The current local validation was performed with Stata 19 on macOS.

## Outputs

The main user-facing outputs are in `results/paper` and `results/appendix`.

Long-form machine-readable table files, Stata logs, setup information, and diagnostic checks are in `results/diagnostics`.

The diagnostics checks cover sample sizes, headline values, generated artifact existence, and Stata availability. They are intended as a confidence check and troubleshooting aid, not as the main purpose of the repository.
