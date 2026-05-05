from __future__ import annotations

import argparse
import json

from src.analysis.figures import build as build_figures
from src.analysis.run_stata_tables import run as run_stata_tables
from src.analysis.tables_appendix import build as build_appendix_summary
from src.data.assemble import build as build_data
from src.environment import collect_setup
from src.stata import StataConfigurationError
from src.verification.checks import run_checks
from src.verification.correspondence import build as build_correspondence
from src.verification.report import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replicate the analysis for Efficiency Wages with Motivated Agents."
    )
    parser.add_argument(
        "--check-setup",
        action="store_true",
        help="Check Python and Stata setup without rebuilding replication outputs.",
    )
    parser.add_argument(
        "--skip-stata",
        action="store_true",
        help="Rebuild Python outputs and report, but do not rerun Stata regression tables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup = collect_setup()

    if args.check_setup:
        report = build_report(
            setup=setup,
            verification=None,
            mode="check-setup",
            stata_tables_rerun=False,
        )
        print(json.dumps(setup, indent=2))
        print(f"Setup report written to {report}")
        return

    build_data()
    build_figures()
    if args.skip_stata:
        build_appendix_summary()
    else:
        try:
            run_stata_tables()
        except StataConfigurationError as error:
            report = build_report(
                setup=setup,
                verification=None,
                mode="failed-stata-setup",
                stata_tables_rerun=False,
            )
            raise SystemExit(f"{error}\nSetup report written to {report}.") from None
    build_correspondence()

    verification = run_checks(
        require_stata=not args.skip_stata,
        require_stata_tables=not args.skip_stata,
    )
    report = build_report(
        setup=setup,
        verification=verification,
        mode="skip-stata" if args.skip_stata else "full",
        stata_tables_rerun=not args.skip_stata,
    )
    if not verification["pass"]:
        raise SystemExit(f"Replication verification failed. See {report}.")
    print(f"Replication pipeline completed. See {report}.")


if __name__ == "__main__":
    main()
