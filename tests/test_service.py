"""Tests for the FastAPI service, with a fake engine so no model is needed."""
import pytest
from fastapi.testclient import TestClient

from service.app import create_app


class FakeEngine:
    def __init__(self, cat_logits, pri_logits):
        self.logits = {"category": cat_logits, "priority": pri_logits}

    def predict(self, email, **kwargs):
        return {"raw": "{}", "schema_valid": True,
                "pred": {"category": "Technical Support", "priority": "high", "account_id": "4278"},
                "logits": self.logits, "conf": {"account_id": 0.97},
                "prompt_s": 0.1, "modes": {"native": {"gen_s": 0.2}}}


class FakeTeacher:
    calls = 0

    def label(self, email):
        FakeTeacher.calls += 1
        return {"label": {"category": "Billing & Payments", "priority": "medium", "account_id": None},
                "served_model": "deepseek-flash"}


SETTINGS = {"threshold": 0.8, "temperatures": {"category": 1.0, "priority": 1.0}}
SURE = FakeEngine([9, 0, 0, 0, 0], [9, 0, 0])
UNSURE = FakeEngine([1, 0.9, 0, 0, 0], [9, 0, 0])


def test_confident_ticket_stays_local():
    client = TestClient(create_app(engine=SURE, teacher=None, settings=SETTINGS))
    body = client.post("/triage", json={"email": "Subject: x\n\nEmail: server down"}).json()
    assert body["escalate"] is False
    assert body["answered_by"] == "small model"
    assert body["triage"]["priority"] == "high"
    assert body["confidence"]["category"] > 0.99


def test_unsure_ticket_escalates_without_teacher():
    client = TestClient(create_app(engine=UNSURE, teacher=None, settings=SETTINGS))
    body = client.post("/triage", json={"email": "hello"}).json()
    assert body["escalate"] is True
    assert body["answered_by"] == "small model, teacher not configured"


def test_unsure_ticket_uses_teacher_when_configured():
    client = TestClient(create_app(engine=UNSURE, teacher=FakeTeacher(), settings=SETTINGS))
    body = client.post("/triage", json={"email": "hello"}).json()
    assert body["answered_by"] == "teacher"
    assert body["triage"]["category"] == "Billing & Payments"
    assert body["small_model"]["category"] == "Technical Support"


def test_empty_email_is_rejected():
    client = TestClient(create_app(engine=SURE, teacher=None, settings=SETTINGS))
    assert client.post("/triage", json={"email": "  "}).status_code == 422


def test_health():
    client = TestClient(create_app(engine=SURE, teacher=None, settings=SETTINGS))
    assert client.get("/health").json()["ok"] is True
