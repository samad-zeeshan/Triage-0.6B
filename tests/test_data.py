"""Tests for loading, splitting and augmenting the ticket data."""
import json

import pytest

from triage import data
from conftest import ROOT, SOURCE_CSV


def test_committed_splits_have_expected_sizes():
    assert len(data.load_chat(ROOT / "data/test_chat.jsonl")) == 1200
    assert len(data.load_chat(ROOT / "data/train_chat.jsonl")) == 2500


def test_load_chat_separates_email_and_gold():
    row = data.load_chat(ROOT / "data/test_chat.jsonl")[0]
    assert row["id"] == "test-0000"
    assert row["email"].startswith("Subject: ")
    assert set(row["gold"]) == {"category", "priority", "account_id"}
    assert row["gold"]["category"] in data.CATEGORIES
    assert row["gold"]["priority"] in data.PRIORITIES


def test_prompt_matches_training_template():
    text = data.prompt("Subject: x\n\nEmail: y")
    assert text.startswith("<|im_start|>system\n" + data.SYSTEM)
    # Training used enable_thinking=False, which leaves an empty think block.
    assert text.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")


def test_trivial_baselines_match_v1():
    gold = [r["gold"] for r in data.load_chat(ROOT / "data/test_chat.jsonl")]
    assert round(100 * sum(g["priority"] == "high" for g in gold) / 1200, 1) == 42.4
    assert round(100 * sum(g["category"] == "Technical Support" for g in gold) / 1200, 1) == 63.8


@pytest.mark.skipif(not SOURCE_CSV.exists(), reason="source CSV not downloaded")
def test_split_and_augment_reproduce_committed_files():
    train, test, val = data.build_splits(data.load_source(SOURCE_CSV))
    assert (len(train), len(test), len(val)) == (2500, 1200, 600)
    committed = [r["email"] for r in data.load_chat(ROOT / "data/test_chat.jsonl")]
    assert [data.email_text(r.subject, r.body_aug) for r in test.itertuples()] == committed
    committed = [r["email"] for r in data.load_chat(ROOT / "data/train_chat.jsonl")]
    assert [data.email_text(r.subject, r.body_aug) for r in train.itertuples()] == committed


@pytest.mark.skipif(not SOURCE_CSV.exists(), reason="source CSV not downloaded")
def test_validation_split_is_disjoint_from_train_and_test():
    train, test, val = data.build_splits(data.load_source(SOURCE_CSV))
    seen = set(train.body) | set(test.body)
    assert not seen & set(val.body)


def test_parse_output_strict_and_lenient():
    ok = '{"category": "Product Support", "priority": "low", "account_id": null}'
    assert data.parse_output(ok)["schema_valid"]
    essay = 'Sure! {"priority": "High", "category": "Billing"} hope that helps'
    p = data.parse_output(essay)
    assert not p["schema_valid"] and not p["json_valid"]
    assert p["fields"]["priority"] == "high"
    assert p["fields"]["category"] == "Billing"
    assert data.parse_output("no json here")["fields"] == {
        "category": None, "priority": None, "account_id": None}


def test_schema_rejects_extra_keys_and_bad_enum():
    bad = json.dumps({"category": "Sales", "priority": "low", "account_id": None})
    assert not data.parse_output(bad)["schema_valid"]
    extra = json.dumps({"category": "Product Support", "priority": "low",
                        "account_id": None, "note": "x"})
    assert not data.parse_output(extra)["schema_valid"]
