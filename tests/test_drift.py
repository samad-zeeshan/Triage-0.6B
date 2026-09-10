"""Drift checks: results must rebuild from the recorded runs, and the README must match the results."""
import json
import re

import pytest

from triage import eval as ev
from triage import readme
from conftest import ROOT

RESULTS = sorted((ROOT / "eval/results").glob("*.json"))


@pytest.mark.parametrize("path", RESULTS, ids=[p.stem for p in RESULTS])
def test_result_file_rebuilds_from_runs(path):
    builders = {"headline": ev.headline, "decoding": ev.decoding, "quantization": ev.quantization,
                "trust": ev.trust, "geometry": ev.geometry,
                "calibration": lambda: ev.calibration(ev.deployed()), "cascade": lambda: ev.cascade_result(ev.deployed())}
    rebuilt = json.loads(json.dumps(builders[path.stem]()))
    committed = json.loads(path.read_text(encoding="utf-8"))
    assert rebuilt == committed


def test_readme_tables_match_results():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.render(text) == text


def test_readme_opening_numbers_match_results():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    opener = text.split("\n\n")[1]
    h = json.loads((ROOT / "eval/results/headline.json").read_text(encoding="utf-8"))
    claimed = [int(x) for x in re.findall(r"(\d+) percent", opener)]
    assert claimed == [round(h["tuned"]["priority"]["acc"])]
    assert h["base"]["priority"]["acc"] < h["trivial"]["priority"]["acc"]


def test_readme_is_short_and_the_only_markdown_file():
    assert len((ROOT / "README.md").read_text(encoding="utf-8").splitlines()) < 120
    md = [p for p in ROOT.rglob("*.md") if not any(s in p.parts for s in (".venv", ".cache", "out", "node_modules", ".pytest_cache"))]
    assert [p.name for p in md] == ["README.md"]
