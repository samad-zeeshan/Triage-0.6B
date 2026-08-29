"""Tests for the trust suite inputs and scoring rules."""
from triage import trust


def test_typo_noise_is_seeded_and_changes_text():
    text = "Subject: Login broken\n\nEmail: I cannot log in to the dashboard since this morning."
    a, b = trust.typos(text, seed=3), trust.typos(text, seed=3)
    assert a == b and a != text
    assert a.startswith("Subject: ")


def test_pii_echo_detects_planted_values():
    out = '{"category": "Billing & Payments", "priority": "high", "account_id": "4111111111111111"}'
    assert trust.pii_echo(out) == ["card"]
    assert trust.pii_echo('{"account_id": "8051"}') == []
    assert "email" in trust.pii_echo("contact jane.doe@example.com")


def test_suites_have_fixed_sizes():
    assert len(trust.OFF_TASK) == 30
    assert len(trust.INJECTION_LINES) >= 3


def test_account_prefix_split():
    email = "Subject: x\n\nEmail: Broken again. For reference, my account ends in 4278."
    prefix, acct = trust.split_account(email)
    assert acct == "4278"
    assert prefix.endswith("my account ends in")
    assert trust.split_account("Subject: x\n\nEmail: no id here") == (None, None)
