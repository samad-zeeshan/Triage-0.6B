"""Tests for the cached teacher labeller, with a fake client instead of the API."""
import json
from types import SimpleNamespace

import pytest

from triage import label


class FakeClient:
    def __init__(self, reply):
        self.calls = 0
        self.reply = reply
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls += 1
        msg = SimpleNamespace(content=self.reply)
        usage = SimpleNamespace(prompt_tokens=300, completion_tokens=20)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=usage,
                               model="deepseek-flash")


CFG = {"model": "deepseek-chat", "price_input_per_m": 0.30, "price_output_per_m": 1.20,
       "workers": 2, "key_env": "NOPE"}


def test_cache_prevents_second_call(tmp_path):
    reply = json.dumps({"category": "Product Support", "priority": "low", "account_id": None})
    client = FakeClient(reply)
    t = label.Teacher(CFG, cache=tmp_path / "cache.jsonl", client=client)
    first = t.label("Subject: a\n\nEmail: b")
    again = label.Teacher(CFG, cache=tmp_path / "cache.jsonl", client=client).label("Subject: a\n\nEmail: b")
    assert client.calls == 1
    assert first["label"] == again["label"]
    assert first["served_model"] == "deepseek-flash"


def test_cost_uses_configured_prices():
    assert label.cost_usd(1_000_000, 1_000_000, CFG) == pytest.approx(1.50)
    assert label.cost_usd(300, 20, CFG) == pytest.approx(0.000114)


def test_missing_key_fails_with_clear_message(monkeypatch):
    monkeypatch.delenv("NOPE", raising=False)
    with pytest.raises(RuntimeError, match="NOPE"):
        label.Teacher(CFG, cache=None).label("x")


def test_bad_json_reply_is_recorded_as_none(tmp_path):
    t = label.Teacher(CFG, cache=tmp_path / "c.jsonl", client=FakeClient("not json"))
    assert t.label("Subject: a\n\nEmail: b")["label"] is None
