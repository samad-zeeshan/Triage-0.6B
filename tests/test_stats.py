"""Tests for accuracy, bootstrap intervals and the McNemar test."""
import numpy as np
import pytest

from triage import stats
from conftest import ROOT


def test_bootstrap_interval_brackets_the_mean_and_is_seeded():
    x = np.array([1] * 870 + [0] * 130)
    lo, hi = stats.bootstrap_ci(x)
    assert lo < 0.87 < hi
    assert (lo, hi) == stats.bootstrap_ci(x)
    assert 0.84 < lo and hi < 0.90


def test_paired_difference_interval():
    rng = np.random.default_rng(1)
    a = rng.random(1200) < 0.87
    b = rng.random(1200) < 0.38
    lo, hi = stats.paired_diff_ci(a.astype(int), b.astype(int))
    assert lo > 0.40 and hi < 0.56


def test_mcnemar_exact():
    assert stats.mcnemar(np.array([1, 0] * 5), np.array([1, 0] * 5)) == 1.0
    a = np.array([1] * 10 + [0] * 5)
    b = np.array([0] * 10 + [0] * 5)
    assert stats.mcnemar(a, b) == pytest.approx(2 / 1024)
    big = stats.mcnemar(np.array([1] * 600 + [0] * 600), np.array([0] * 600 + [0] * 600))
    assert 0 <= big < 1e-100


def test_v1_file_parses_to_published_numbers():
    v1 = stats.parse_v1(ROOT / "eval/v1/confusion_matrices.txt")
    assert v1 == {"baseline_priority": 42.4, "base_priority": 38.3, "base_category": 64.2,
                  "tuned_priority": 87.3, "tuned_category": 89.7,
                  "base_valid_json": 100.0, "tuned_valid_json": 100.0}
