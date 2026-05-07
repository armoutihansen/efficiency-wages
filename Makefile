.PHONY: all setup data figures tables clean-derived

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

clean-derived:
	rm -f data/derived/*.csv data/derived/*.json results/paper/tables/* results/paper/figures/* results/appendix/tables/* results/appendix/figures/* results/_intermediate/tables/* results/_intermediate/figures/* results/_intermediate/logs/*
