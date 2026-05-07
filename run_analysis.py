from __future__ import annotations

import argparse
import json

from src.analysis.figures import build as build_figures
from src.analysis.run_stata_tables import run as run_stata_tables
from src.data.assemble import build as build_data
from src.environment import collect_setup
from src.stata import StataConfigurationError, StataExecutionError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the analysis for Efficiency Wages with Motivated Agents."
    )
    parser.add_argument(
        "--check-setup",
        action="store_true",
        help="Check Python and Stata setup without rebuilding analysis outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup = collect_setup()

    if args.check_setup:
        print(json.dumps(setup, indent=2))
        return

    build_data()
    build_figures()
    try:
        run_stata_tables()
    except (StataConfigurationError, StataExecutionError) as error:
        raise SystemExit(str(error)) from None
    print("Analysis completed.")
    print("Inspect generated tables and figures in results/paper and results/appendix.")


if __name__ == "__main__":
    main()
