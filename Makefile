.PHONY: all data figures tables correspondence verify clean-derived

all: data figures tables correspondence verify

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

clean-derived:
	rm -f data/derived/*.csv data/derived/*.json outputs/tables/*.csv outputs/tables/*.dta outputs/figures/*.png outputs/figures/*.json outputs/*.json outputs/*.md outputs/logs/*.log
