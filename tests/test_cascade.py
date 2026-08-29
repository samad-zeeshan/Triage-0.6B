"""Tests for the confidence-threshold cascade."""
import numpy as np
import pytest

from triage import cascade


def test_threshold_zero_keeps_everything_and_one_escalates_everything():
    conf = np.array([0.2, 0.6, 0.9])
    student = np.array([0, 1, 1])
    teacher = np.array([1, 1, 0])
    none = cascade.apply(conf, student, teacher, 0.0)
    assert none["escalated"] == 0.0 and none["acc"] == pytest.approx(2 / 3)
    every = cascade.apply(conf, student, teacher, 1.01)
    assert every["escalated"] == 1.0 and every["acc"] == pytest.approx(2 / 3)


def test_escalating_the_unsure_ticket_fixes_it():
    conf = np.array([0.2, 0.6, 0.9])
    r = cascade.apply(conf, np.array([0, 1, 1]), np.array([1, 1, 0]), 0.5)
    assert r["escalated"] == pytest.approx(1 / 3)
    assert r["acc"] == 1.0
    assert r["kept_acc"] == 1.0


def test_choose_threshold_meets_target_on_kept_tickets():
    rng = np.random.default_rng(0)
    conf = rng.random(2000)
    correct = rng.random(2000) < conf
    t = cascade.choose_threshold(conf, correct, target=0.9)
    kept = conf >= t
    assert correct[kept].mean() >= 0.9
    assert cascade.choose_threshold(conf, correct, target=0.9) == t


def test_cost_scales_with_escalation():
    assert cascade.cost_per_1000(0.25, 0.0001) == pytest.approx(0.025)
