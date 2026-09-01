"""Tests for the result builder helpers on hand-made run rows."""
import numpy as np

from triage import eval as ev


def _row(i, pred, gold, logits=None):
    return {"id": f"test-{i:04d}", "gold": gold,
            "modes": {"native": {"pred": pred, "schema_valid": True, "json_valid": True}},
            "logits": logits or {"category": [5, 0, 0, 0, 0], "priority": [0, 5, 0]}}


GOLD = {"category": "Technical Support", "priority": "medium", "account_id": None}


def test_correct_and_v1_validity_rule():
    rows = [_row(0, dict(GOLD), GOLD),
            _row(1, {"category": None, "priority": "high", "account_id": None}, GOLD)]
    assert list(ev.correct(rows, "priority")) == [1, 0]
    assert list(ev.correct(rows, "account_id")) == [1, 1]
    assert list(ev.lenient_valid(rows)) == [1, 0]


def test_ticket_confidence_is_the_weaker_field():
    rows = [_row(0, dict(GOLD), GOLD, {"category": [5, 0, 0, 0, 0], "priority": [0, 0.1, 0]})]
    conf = ev._ticket_conf(ev._items(rows), {"category": 1.0, "priority": 1.0})
    p = np.exp(0.1) / (np.exp(0.1) + 2)
    assert np.isclose(conf[0], p)


def test_invalid_prediction_has_zero_confidence():
    rows = [_row(0, {"category": "Sales", "priority": "medium", "account_id": None}, GOLD)]
    assert ev._ticket_conf(ev._items(rows), {"category": 1.0, "priority": 1.0})[0] == 0.0
