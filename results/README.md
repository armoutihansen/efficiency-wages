# Results

This folder contains generated analysis outputs.

- `paper/tables/`: main paper Tables 2-4 as `.tex` and `.csv`.
- `paper/figures/`: main paper Figures 2-4 as `.png`.
- `appendix/tables/`: online appendix Tables A.1-A.9 as `.tex` and `.csv`.
- `appendix/figures/`: online appendix Figures A.1-A.8 as `.png`.

Regenerate these files by running `analysis.ipynb` or `uv run python run_analysis.py` from the repository root.

The final results in `paper/` and `appendix/` are committed so the tables and figures can be inspected without rerunning the analysis. Temporary Stata logs and machine-readable intermediate files are generated under `results/_intermediate/` and ignored by git.
