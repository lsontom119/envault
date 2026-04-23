"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_vaults, format_diff, DiffEntry


OLD = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "old_secret"}
NEW = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "abc123"}


def test_diff_detects_added_key():
    entries = diff_vaults(OLD, NEW)
    added = [e for e in entries if e.status == "added"]
    assert any(e.key == "API_KEY" for e in added)


def test_diff_detects_removed_key():
    entries = diff_vaults(OLD, NEW)
    removed = [e for e in entries if e.status == "removed"]
    assert any(e.key == "SECRET" for e in removed)


def test_diff_detects_changed_key():
    entries = diff_vaults(OLD, NEW)
    changed = [e for e in entries if e.status == "changed"]
    assert any(e.key == "DB_HOST" for e in changed)
    entry = next(e for e in changed if e.key == "DB_HOST")
    assert entry.old_value == "localhost"
    assert entry.new_value == "prod.db"


def test_diff_unchanged_hidden_by_default():
    entries = diff_vaults(OLD, NEW)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert unchanged == []


def test_diff_unchanged_shown_when_requested():
    entries = diff_vaults(OLD, NEW, show_unchanged=True)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert any(e.key == "DB_PORT" for e in unchanged)


def test_diff_identical_vaults_returns_empty():
    entries = diff_vaults(OLD, OLD)
    assert entries == []


def test_format_diff_masks_values_by_default():
    entries = diff_vaults(OLD, NEW)
    output = format_diff(entries)
    assert "old_secret" not in output
    assert "abc123" not in output
    assert "***" in output


def test_format_diff_shows_values_when_requested():
    entries = diff_vaults(OLD, NEW)
    output = format_diff(entries, mask_values=False)
    assert "old_secret" in output
    assert "abc123" in output


def test_format_diff_empty_returns_no_differences():
    output = format_diff([])
    assert output == "No differences found."


def test_format_diff_contains_symbols():
    entries = diff_vaults(OLD, NEW)
    output = format_diff(entries)
    assert "+" in output  # added
    assert "-" in output  # removed
    assert "~" in output  # changed


def test_diff_results_sorted_by_key():
    entries = diff_vaults({"Z": "1", "A": "2"}, {"Z": "1", "B": "3"})
    keys = [e.key for e in entries]
    assert keys == sorted(keys)
