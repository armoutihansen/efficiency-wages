# Outputs

This folder contains generated replication artifacts.

- `replication_report.html`: researcher-facing report with setup, checks, tables, figures, and correspondence.
- `verification_report.json`: machine-readable pass/fail checks.
- `correspondence.md`: map from paper and appendix artifacts to scripts and outputs.
- `tables/`: generated table data.
- `figures/`: generated figure images.

These outputs are committed so readers can inspect the results without rerunning the full pipeline. Running `uv run python replicate.py` regenerates them.
