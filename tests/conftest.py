"""Shared fixtures and paths for the test suite."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT / ".cache" / "tickets.csv"
MODELS = ROOT / "models"


def need_model(name: str) -> Path:
    path = MODELS / name
    if not path.exists():
        pytest.skip(f"{name} not downloaded, run `python -m triage.export fetch`")
    return path
