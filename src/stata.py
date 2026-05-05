from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from src.replication_paths import LOGS, ROOT


MIN_STATA_VERSION = 17.0


class StataConfigurationError(RuntimeError):
    pass


class StataExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class StataInfo:
    executable: str | None
    source: str | None
    version: str | None
    minimum_required: str
    available: bool
    usable: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _candidate_names() -> list[str]:
    return [
        "stata-se",
        "stata-mp",
        "stata-be",
        "stata",
        "StataSE-64.exe",
        "StataMP-64.exe",
        "StataBE-64.exe",
        "StataSE.exe",
        "StataMP.exe",
        "StataBE.exe",
        "Stata.exe",
    ]


def _common_install_paths() -> list[Path]:
    paths = [
        Path("/Applications/Stata/StataSE.app/Contents/MacOS/stata-se"),
        Path("/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp"),
        Path("/Applications/Stata/StataBE.app/Contents/MacOS/stata-be"),
        Path("/usr/local/stata/stata-se"),
        Path("/usr/local/stata/stata-mp"),
        Path("/usr/local/stata/stata-be"),
        Path("/usr/local/bin/stata-se"),
        Path("/usr/local/bin/stata-mp"),
        Path("/usr/local/bin/stata-be"),
    ]

    program_roots = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
    ]
    windows_executables = [
        "StataSE-64.exe",
        "StataMP-64.exe",
        "StataBE-64.exe",
        "StataSE.exe",
        "StataMP.exe",
        "StataBE.exe",
        "Stata.exe",
    ]
    for root in [Path(value) for value in program_roots if value]:
        for version in range(25, 16, -1):
            for executable in windows_executables:
                paths.append(root / f"Stata{version}" / executable)
                paths.append(root / "Stata" / executable)
    return paths


def _find_executable() -> tuple[Path | None, str | None, str | None]:
    env_path = os.environ.get("STATA_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_file():
            if platform.system() != "Windows" and not os.access(candidate, os.X_OK):
                return None, "STATA_PATH", f"STATA_PATH points to a non-executable file: {candidate}"
            return candidate, "STATA_PATH", None
        if candidate.exists():
            return None, "STATA_PATH", f"STATA_PATH points to a directory, not an executable: {candidate}"
        return None, "STATA_PATH", f"STATA_PATH points to a missing file: {candidate}"

    for name in _candidate_names():
        found = shutil.which(name)
        if found:
            return Path(found), "PATH", None

    for candidate in _common_install_paths():
        if candidate.exists():
            return candidate, "common install path", None

    return None, None, None


def _stata_command(executable: Path, command: str) -> list[str]:
    if platform.system() == "Windows":
        return [str(executable), "/e", command]
    return [str(executable), "-q", command]


def _parse_version(text: str) -> str | None:
    for line in text.splitlines():
        match = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\b", line.strip())
        if match:
            return match.group(1)
    return None


def _detect_version(executable: Path) -> str | None:
    completed = subprocess.run(
        _stata_command(executable, "display c(stata_version)"),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    version = _parse_version(completed.stdout)
    if version:
        return version

    LOGS.mkdir(parents=True, exist_ok=True)
    version_do = LOGS / "detect_stata_version.do"
    version_log = LOGS / "detect_stata_version.log"
    version_do.write_text(
        "\n".join(
            [
                "version 17",
                "set more off",
                f'log using "{version_log.as_posix()}", replace text',
                "display c(stata_version)",
                "log close",
                "exit, clear",
            ]
        )
        + "\n"
    )
    subprocess.run(
        _stata_command(executable, f'do "{version_do.as_posix()}"'),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if version_log.exists():
        return _parse_version(version_log.read_text(errors="replace"))
    return None


def resolve_stata() -> StataInfo:
    executable, source, error = _find_executable()
    minimum = f"{MIN_STATA_VERSION:g}"
    if executable is None:
        message = error or (
            "Could not find Stata. Install Stata 17 or newer, put the executable on PATH, "
            "or set STATA_PATH to the full executable path."
        )
        return StataInfo(None, source, None, minimum, False, False, message)

    version = _detect_version(executable)
    if version is None:
        return StataInfo(
            str(executable),
            source,
            None,
            minimum,
            True,
            False,
            "Found Stata but could not detect its version.",
        )

    usable = float(version) >= MIN_STATA_VERSION
    message = (
        f"Found Stata {version} at {executable}."
        if usable
        else f"Found Stata {version}, but Stata {minimum} or newer is required."
    )
    return StataInfo(str(executable), source, version, minimum, True, usable, message)


def require_stata() -> StataInfo:
    info = resolve_stata()
    if not info.usable or info.executable is None:
        raise StataConfigurationError(
            f"{info.message}\n"
            "Set STATA_PATH to the full Stata executable path and rerun the command."
        )
    return info


def run_do_file(do_file: str, stdout_name: str) -> StataInfo:
    info = require_stata()
    assert info.executable is not None
    LOGS.mkdir(parents=True, exist_ok=True)
    executable = Path(info.executable)
    command = f'do "{do_file}"'
    completed = subprocess.run(
        _stata_command(executable, command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (LOGS / stdout_name).write_text(completed.stdout)
    if completed.returncode != 0:
        raise StataExecutionError(
            f"Stata table generation failed with exit code {completed.returncode}. "
            f"See {LOGS / stdout_name}."
        )
    return info
