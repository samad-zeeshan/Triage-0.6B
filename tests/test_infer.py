"""Tests for the GGUF inference engine. They need models/ and skip without it."""
import math

import pytest

from triage import data, infer
from conftest import ROOT, need_model




@pytest.fixture(scope="module")
def tuned():
    return infer.Engine(need_model("triage-0.6b-q8_0.gguf"), n_threads=4)


@pytest.fixture(scope="module")
def first():
    return data.load_chat(ROOT / "data/test_chat.jsonl")[0]


def test_native_prediction_matches_gold_on_easy_ticket(tuned, first):
    out = tuned.predict(first["email"])
    assert out["schema_valid"]
    assert out["pred"] == first["gold"]


def test_probabilities_are_normalised(tuned, first):
    out = tuned.predict(first["email"])
    for field, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
        assert set(out["probs"][field]) == set(options)
        assert math.isclose(sum(out["probs"][field].values()), 1.0, rel_tol=1e-6)
        assert 0.0 <= out["conf"][field] <= 1.0
    assert 0.0 <= out["conf"]["account_id"] <= 1.0


def test_decoding_is_deterministic(tuned, first):
    assert tuned.predict(first["email"])["raw"] == tuned.predict(first["email"])["raw"]


@pytest.mark.parametrize("mode", ["outlines", "xgrammar"])
def test_constrained_modes_always_meet_schema(tuned, mode):
    out = tuned.predict("What is the capital of France? Answer in one word.", modes=[mode],
                        score=False)
    assert out["modes"][mode]["schema_valid"]


def test_constrained_modes_fix_base_model_structure():
    base = infer.Engine(need_model("qwen3-0.6b-base-q8_0.gguf"), n_threads=4)
    email = "Subject: Invoice\n\nEmail: I was charged twice this month, please refund one."
    out = base.predict(email, modes=["native", "outlines", "xgrammar"], score=False)
    assert out["modes"]["outlines"]["schema_valid"]
    assert out["modes"]["xgrammar"]["schema_valid"]


def test_missing_model_file_names_the_file(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/models.yaml").write_text("models:\n  q8_0:\n    file: nope.gguf\n")
    with pytest.raises(FileNotFoundError, match="nope.gguf"):
        infer.model_path("q8_0", root=tmp_path)
