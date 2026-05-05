.PHONY: all setup data figures tables correspondence verify report clean-derived

all:
	uv run python run_analysis.py

setup:
	uv run python run_analysis.py --check-setup

data:
	uv run python -m src.data.assemble

figures: data
	uv run python -m src.analysis.figures

tables: data
	uv run python -m src.analysis.run_stata_tables

correspondence:
	uv run python -m src.verification.correspondence

verify:
	uv run python -m src.verification.checks

report:
	uv run python run_analysis.py --skip-stata

clean-derived:
	rm -f data/derived/*.csv data/derived/*.json results/paper/tables/* results/paper/figures/* results/appendix/tables/* results/appendix/figures/* results/diagnostics/*.json results/diagnostics/*.md results/diagnostics/*.html results/diagnostics/tables/* results/diagnostics/figures/* results/diagnostics/logs/*
