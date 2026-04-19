"""Tests for envault.audit module."""

import pytest
from envault.audit import record_event, get_events, clear_events


@pytest.fixture(autouse=True)
def isolated_audit(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.audit._get_audit_log_path", lambda vault_dir=None: tmp_path / ".envault_audit.json")
    yield
    clear_events()


def test_record_event_creates_log(tmp_path):
    record_event("set", key="API_KEY")
    events = get_events()
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["key"] == "API_KEY"


def test_record_event_without_key():
    record_event("push")
    events = get_events()
    assert len(events) == 1
    assert "key" not in events[0]


def test_multiple_events_appended():
    record_event("set", key="FOO")
    record_event("set", key="BAR")
    record_event("get", key="FOO")
    events = get_events()
    assert len(events) == 3
    assert events[0]["key"] == "FOO"
    assert events[2]["action"] == "get"


def test_get_events_returns_empty_when_no_log():
    events = get_events()
    assert events == []


def test_event_has_timestamp():
    record_event("delete", key="SECRET")
    events = get_events()
    assert "timestamp" in events[0]
    assert "T" in events[0]["timestamp"]  # ISO format check


def test_clear_events_removes_log(tmp_path):
    record_event("set", key="X")
    clear_events()
    assert get_events() == []


def test_corrupted_log_resets_gracefully(tmp_path, monkeypatch):
    log_path = tmp_path / ".envault_audit.json"
    log_path.write_text("not valid json")
    monkeypatch.setattr("envault.audit._get_audit_log_path", lambda vault_dir=None: log_path)
    record_event("set", key="RECOVER")
    events = get_events()
    assert len(events) == 1
