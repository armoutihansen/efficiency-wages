from __future__ import annotations

from src.analysis.figures import build as build_figures
from src.analysis.run_stata_tables import run as run_stata_tables
from src.data.assemble import build as build_data
from src.verification.checks import run_checks
from src.verification.correspondence import build as build_correspondence


def main() -> None:
    build_data()
    build_figures()
    run_stata_tables()
    build_correspondence()
    report = run_checks()
    if not report["pass"]:
        raise SystemExit("Replication verification failed. See outputs/verification_report.json.")
    print("Replication pipeline completed. See outputs/ for generated artifacts.")


if __name__ == "__main__":
    main()
