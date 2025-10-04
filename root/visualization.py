"""Compatibility wrapper for the visualization CLI.

Running ``python root/visualization.py`` forwards arguments to the
:mod:`nba_predictor.visualization` entry point. This keeps older instructions
working while avoiding optional dependencies such as Plotly.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _suggest_requirements() -> str:
    requirements = Path("requirements.txt")
    if requirements.exists():
        return (
            "Install dependencies with `pip install -r requirements.txt` "
            "before running the visualization command."
        )
    return "Install the project dependencies before running the visualization command."


def main(argv: Optional[Iterable[str]] = None) -> None:
    try:
        from nba_predictor.visualization import main as cli_main
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive guard
        missing = exc.name
        hint = _suggest_requirements()
        raise SystemExit(
            f"Unable to import required module '{missing}'. {hint}"
        ) from exc

    cli_main(list(argv) if argv is not None else None)


if __name__ == "__main__":
    main(sys.argv[1:])
