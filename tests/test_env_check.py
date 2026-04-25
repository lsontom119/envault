"""Tests for envault.env_check."""
from __future__ import annotations

import pytest

from envault.env_check import (
    CheckReport,
    CheckResult,
    EnvCheckError,
    check_pattern,
    check_required,
    run_checks,
)


SAMPLE_VAULT: dict[str, str] = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "s3cr3t!",
    "PORT": "8080",
    "EMPTY_VAR": "",
}


# --- check_required ---

def test_check_required_all_present():
    results = check_required(SAMPLE_VAULT, ["DATABASE_URL", "SECRET_KEY"])
    assert all(r.passed for r in results)


def test_check_required_missing_key():
    results = check_required(SAMPLE_VAULT, ["MISSING_KEY"])
    assert len(results) == 1
    assert not results[0].passed
    assert "MISSING_KEY" in results[0].message


def test_check_required_empty_value_fails():
    results = check_required(SAMPLE_VAULT, ["EMPTY_VAR"])
    assert not results[0].passed


def test_check_required_mixed_results():
    results = check_required(SAMPLE_VAULT, ["DATABASE_URL", "MISSING"])
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    assert len(passed) == 1
    assert len(failed) == 1


# --- check_pattern ---

def test_check_pattern_match():
    result = check_pattern(SAMPLE_VAULT, "PORT", r"\d+")
    assert result.passed


def test_check_pattern_no_match():
    result = check_pattern(SAMPLE_VAULT, "PORT", r"[a-z]+")
    assert not result.passed
    assert "PORT" in result.message


def test_check_pattern_missing_key():
    result = check_pattern(SAMPLE_VAULT, "NOT_THERE", r".*")
    assert not result.passed
    assert "not found" in result.message


# --- CheckReport ---

def test_check_report_ok_when_all_pass():
    report = CheckReport(results=[CheckResult("K", True, "ok")])
    assert report.ok
    assert len(report.passed) == 1
    assert len(report.failed) == 0


def test_check_report_not_ok_when_any_fail():
    report = CheckReport(
        results=[
            CheckResult("A", True, "ok"),
            CheckResult("B", False, "bad"),
        ]
    )
    assert not report.ok
    assert len(report.failed) == 1


# --- run_checks ---

def test_run_checks_raises_on_bad_vault(tmp_path):
    with pytest.raises(EnvCheckError):
        run_checks("wrongpassword", required_keys=["X"], vault_dir=str(tmp_path))


def test_run_checks_with_mock_load(monkeypatch):
    monkeypatch.setattr("envault.env_check.load_vault", lambda pw, **kw: SAMPLE_VAULT)
    report = run_checks("any", required_keys=["DATABASE_URL"], patterns={"PORT": r"\d+"})
    assert report.ok
    assert len(report.results) == 2


def test_run_checks_pattern_fail(monkeypatch):
    monkeypatch.setattr("envault.env_check.load_vault", lambda pw, **kw: SAMPLE_VAULT)
    report = run_checks("any", patterns={"SECRET_KEY": r"\d+"})
    assert not report.ok
