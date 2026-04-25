"""Tests for envault.history module."""

import time
import pytest
from pathlib import Path
from envault.history import (
    record_change,
    get_history,
    clear_history,
    HistoryError,
    MAX_HISTORY_ENTRIES,
)


@pytest.fixture
def vault_env(tmp_path):
    vault_path = str(tmp_path / "vault" / ".envault")
    Path(vault_path).parent.mkdir(parents=True, exist_ok=True)
    Path(vault_path).write_bytes(b"fake")
    return vault_path


def test_record_and_retrieve(vault_env):
    record_change(vault_env, "set", "API_KEY")
    entries = get_history(vault_env)
    assert len(entries) == 1
    assert entries[0].action == "set"
    assert entries[0].key == "API_KEY"


def test_record_without_key(vault_env):
    record_change(vault_env, "rotate")
    entries = get_history(vault_env)
    assert entries[0].key is None
    assert entries[0].action == "rotate"


def test_multiple_entries_newest_first(vault_env):
    record_change(vault_env, "set", "A")
    time.sleep(0.01)
    record_change(vault_env, "set", "B")
    entries = get_history(vault_env)
    assert entries[0].key == "B"
    assert entries[1].key == "A"


def test_get_history_empty_when_no_log(vault_env):
    entries = get_history(vault_env)
    assert entries == []


def test_clear_removes_history(vault_env):
    record_change(vault_env, "set", "X")
    clear_history(vault_env)
    assert get_history(vault_env) == []


def test_clear_no_error_when_no_log(vault_env):
    # Should not raise even if no history file exists
    clear_history(vault_env)


def test_limit_respected(vault_env):
    for i in range(10):
        record_change(vault_env, "set", f"KEY_{i}")
    entries = get_history(vault_env, limit=3)
    assert len(entries) == 3


def test_max_entries_cap(vault_env):
    for i in range(MAX_HISTORY_ENTRIES + 20):
        record_change(vault_env, "set", f"K{i}")
    entries = get_history(vault_env, limit=MAX_HISTORY_ENTRIES + 100)
    assert len(entries) <= MAX_HISTORY_ENTRIES


def test_formatted_time_is_string(vault_env):
    record_change(vault_env, "import")
    entry = get_history(vault_env)[0]
    ft = entry.formatted_time()
    assert isinstance(ft, str)
    assert len(ft) == 19  # YYYY-MM-DD HH:MM:SS
