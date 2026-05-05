# Technical Notes

## Pipeline

The primary entrypoint is:

```bash
uv run python replicate.py
```

It runs these steps:

1. Collect setup information for Python, dependencies, OS, and Stata.
2. Assemble raw treatment CSV files into derived analysis datasets.
3. Regenerate figures.
4. Regenerate Stata regression tables.
5. Write the paper-to-output correspondence checklist.
6. Run verification checks.
7. Write the HTML replication report.

## Data Inputs

The public replication pipeline uses:

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

The regression CSV files are long-form machine-readable outputs. Each row is one coefficient or constant from one published table/model. The HTML report pivots these into a more readable format.

The figure script also writes `outputs/tables/wage_summary.csv`, which is the summary data used by the wage-comparison figures.

## Verification Scope

The checks cover sample sizes, headline paper results, full Table A.1 summary statistics, representative coefficients from appendix regression tables, generated figure files, and Stata availability. The figure checks verify artifact creation; visual parity remains a manual review step.
