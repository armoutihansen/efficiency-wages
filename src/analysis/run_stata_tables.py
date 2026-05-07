from __future__ import annotations

import json

from src.analysis.format_tables import build as format_tables
from src.analysis.tables_appendix import build as build_appendix_tables
from src.paths import LOGS, TABLES
from src.stata import StataConfigurationError, StataExecutionError, run_do_file


def run() -> dict[str, str]:
    TABLES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    build_appendix_tables()
    info = run_do_file("src/analysis/tables_main.do", "run_stata_main_tables_stdout.log")
    run_do_file("src/analysis/tables_appendix.do", "run_stata_appendix_tables_stdout.log")
    formatted = format_tables()
    return {
        "stata": info.executable or "",
        "stata_version": info.version or "",
        "main_results": str(TABLES / "main_tables_results.csv"),
        "appendix_results": str(TABLES / "appendix_tables_results.csv"),
        "appendix_summary_statistics": str(TABLES / "appendix_table_a1_summary_statistics.csv"),
        "log": str(LOGS / "stata_main_tables.log"),
        "appendix_log": str(LOGS / "stata_appendix_tables.log"),
        "formatted_tables": json.dumps(formatted),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(run(), indent=2))
    except (StataConfigurationError, StataExecutionError) as error:
        raise SystemExit(str(error)) from None
