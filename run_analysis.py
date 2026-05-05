from __future__ import annotations

import argparse
import json

from src.analysis.figures import build as build_figures
from src.analysis.format_tables import build as format_tables
from src.analysis.run_stata_tables import run as run_stata_tables
from src.analysis.tables_appendix import build as build_appendix_summary
from src.data.assemble import build as build_data
from src.environment import collect_setup
from src.replication_paths import OUTPUTS
from src.stata import StataConfigurationError, StataExecutionError
from src.verification.checks import run_checks
from src.verification.correspondence import build as build_correspondence
from src.verification.report import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the analysis for Efficiency Wages with Motivated Agents."
    )
    parser.add_argument(
        "--check-setup",
        action="store_true",
        help="Check Python and Stata setup without rebuilding analysis outputs.",
    )
    parser.add_argument(
        "--skip-stata",
        action="store_true",
        help="Rebuild Python outputs and diagnostics, but do not rerun Stata regression tables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup = collect_setup()

    if args.check_setup:
        diagnostics = build_report(
            setup=setup,
            verification=None,
            mode="check-setup",
            stata_tables_rerun=False,
        )
        print(json.dumps(setup, indent=2))
        print(f"Setup report (JSON) written to {OUTPUTS / 'setup_report.json'}.")
        print(f"Diagnostics written to {diagnostics}.")
        return

    build_data()
    build_figures()
    if args.skip_stata:
        build_appendix_summary()
        format_tables()
    else:
        try:
            run_stata_tables()
        except (StataConfigurationError, StataExecutionError) as error:
            diagnostics = build_report(
                setup=setup,
                verification=None,
                mode="failed-stata-setup",
                stata_tables_rerun=False,
            )
            raise SystemExit(f"{error}\nDiagnostics written to {diagnostics}.") from None
    build_correspondence()

    stata_info = setup.get("stata")
    diagnostics_result = run_checks(
        require_stata=not args.skip_stata,
        require_stata_tables=not args.skip_stata,
        stata_info=stata_info if isinstance(stata_info, dict) else None,
    )
    diagnostics = build_report(
        setup=setup,
        verification=diagnostics_result,
        mode="skip-stata" if args.skip_stata else "full",
        stata_tables_rerun=not args.skip_stata,
    )
    if not diagnostics_result["pass"]:
        raise SystemExit(f"Analysis diagnostics failed. See {diagnostics}.")
    print("Analysis completed.")
    print("Inspect generated tables and figures in results/paper and results/appendix.")
    print(f"Diagnostics written to {diagnostics}.")


if __name__ == "__main__":
    main()
