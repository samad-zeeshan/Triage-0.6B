"""Tests for temperature scaling and calibration metrics."""
import numpy as np
import pytest

from triage import calibrate


def _overconfident(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    true_logits = rng.normal(0, 1.5, size=(n, 3))
    p = np.exp(true_logits) / np.exp(true_logits).sum(1, keepdims=True)
    y = np.array([rng.choice(3, p=row) for row in p])
    return true_logits * 3.0, y


def test_ece_is_zero_for_perfect_calibration():
    conf = np.array([0.8] * 10)
    correct = np.array([1] * 8 + [0] * 2)
    assert calibrate.ece(conf, correct) == pytest.approx(0.0)


def test_ece_and_brier_for_overconfidence():
    conf = np.array([0.99] * 10)
    correct = np.array([1] * 5 + [0] * 5)
    assert calibrate.ece(conf, correct) == pytest.approx(0.49)
    probs = np.array([[0.99, 0.01]] * 10)
    y = np.array([0] * 5 + [1] * 5)
    assert calibrate.brier(probs, y) == pytest.approx((5 * 2 * 0.01**2 + 5 * 2 * 0.99**2) / 10)


def test_temperature_recovers_the_scale():
    logits, y = _overconfident()
    t = calibrate.fit_temperature(logits, y)
    assert 2.4 < t < 3.6


def test_scaling_reduces_ece_on_fresh_data():
    logits, y = _overconfident(seed=1)
    t = calibrate.fit_temperature(logits, y)
    test_logits, test_y = _overconfident(seed=2)
    before = calibrate.field_metrics(test_logits, test_y, 1.0)
    after = calibrate.field_metrics(test_logits, test_y, t)
    assert after["ece"] < before["ece"]


def test_reliability_bins_count_everything():
    conf = np.linspace(0.05, 0.95, 100)
    correct = np.ones(100)
    bins = calibrate.reliability(conf, correct, n_bins=10)
    assert sum(b["n"] for b in bins) == 100
