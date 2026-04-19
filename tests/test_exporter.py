"""Tests for vault export formatting."""

from envault.exporter import to_dotenv, to_export_script

SAMPLE = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/db", "DEBUG": "true"}


def test_export_script_contains_shebang():
    result = to_export_script(SAMPLE)
    assert result.startswith("#!/bin/sh")


def test_export_script_contains_all_keys():
    result = to_export_script(SAMPLE)
    for key in SAMPLE:
        assert f"export {key}=" in result


def test_export_script_values_quoted():
    result = to_export_script({"KEY": "value"})
    assert 'export KEY="value"' in result


def test_export_script_escapes_double_quotes():
    result = to_export_script({"KEY": 'val"ue'})
    assert '\\"' in result


def test_dotenv_contains_all_keys():
    result = to_dotenv(SAMPLE)
    for key in SAMPLE:
        assert f"{key}=" in result


def test_dotenv_values_quoted():
    result = to_dotenv({"KEY": "value"})
    assert 'KEY="value"' in result


def test_dotenv_no_export_keyword():
    result = to_dotenv(SAMPLE)
    assert "export" not in result


def test_dotenv_escapes_double_quotes():
    result = to_dotenv({"KEY": 'say "hello"'})
    assert '\\"' in result
