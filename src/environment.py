from __future__ import annotations

import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone

from src.replication_paths import OUTPUTS
from src.stata import resolve_stata


PYTHON_PACKAGES = ["numpy", "pandas", "matplotlib", "seaborn"]


def collect_setup() -> dict[str, object]:
    packages = {}
    for package in PYTHON_PACKAGES:
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None

    info = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "packages": packages,
        "stata": resolve_stata().to_dict(),
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "setup_report.json").write_text(json.dumps(info, indent=2) + "\n")
    return info
