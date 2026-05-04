from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from src.analysis.tables_appendix import build as build_appendix_tables
from src.replication_paths import LOGS, ROOT, TABLES


STATA_CANDIDATES = [
    Path("/Applications/Stata/StataSE.app/Contents/MacOS/stata-se"),
    Path("/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp"),
    Path("/Applications/Stata/StataBE.app/Contents/MacOS/stata-be"),
]


def find_stata() -> str:
    for candidate in STATA_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    for executable in ["stata-se", "stata-mp", "stata-be", "stata"]:
        found = shutil.which(executable)
        if found:
            return found
    raise FileNotFoundError("Could not find a Stata CLI executable.")


def _run_do_file(stata: str, do_file: str, stdout_name: str) -> None:
    cmd = [stata, "-q", "do", do_file]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (LOGS / stdout_name).write_text(completed.stdout)
    if completed.returncode != 0:
        raise SystemExit(
            f"Stata table generation failed with exit code {completed.returncode}. "
            f"See {LOGS / stdout_name}."
        )


def run() -> dict[str, str]:
    TABLES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    stata = find_stata()
    build_appendix_tables()
    _run_do_file(stata, "src/analysis/tables_main.do", "run_stata_main_tables_stdout.log")
    _run_do_file(stata, "src/analysis/tables_appendix.do", "run_stata_appendix_tables_stdout.log")
    return {
        "stata": stata,
        "main_results": str(TABLES / "main_tables_results.csv"),
        "appendix_results": str(TABLES / "appendix_tables_results.csv"),
        "appendix_summary_statistics": str(TABLES / "appendix_table_a1_summary_statistics.csv"),
        "log": str(LOGS / "stata_main_tables.log"),
        "appendix_log": str(LOGS / "stata_appendix_tables.log"),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
