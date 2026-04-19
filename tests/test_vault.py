"""Tests for vault read/write operations."""

import pytest

from envault.vault import VaultError, delete_var, load_vault, save_vault, set_var

PASSWORD = "test-password-123"


def test_save_and_load_roundtrip(tmp_path):
    vault_file = str(tmp_path / ".envault")
    data = {"API_KEY": "secret", "DB_URL": "postgres://localhost/db"}
    save_vault(PASSWORD, data, vault_file)
    loaded = load_vault(PASSWORD, vault_file)
    assert loaded == data


def test_load_nonexistent_vault_returns_empty(tmp_path):
    vault_file = str(tmp_path / ".envault")
    result = load_vault(PASSWORD, vault_file)
    assert result == {}


def test_load_wrong_password_raises(tmp_path):
    vault_file = str(tmp_path / ".envault")
    save_vault(PASSWORD, {"KEY": "value"}, vault_file)
    with pytest.raises(VaultError):
        load_vault("wrong-password", vault_file)


def test_set_var_adds_key(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var(PASSWORD, "FOO", "bar", vault_file)
    data = load_vault(PASSWORD, vault_file)
    assert data["FOO"] == "bar"


def test_set_var_updates_existing_key(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var(PASSWORD, "FOO", "bar", vault_file)
    set_var(PASSWORD, "FOO", "baz", vault_file)
    data = load_vault(PASSWORD, vault_file)
    assert data["FOO"] == "baz"


def test_delete_var_removes_key(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var(PASSWORD, "FOO", "bar", vault_file)
    delete_var(PASSWORD, "FOO", vault_file)
    data = load_vault(PASSWORD, vault_file)
    assert "FOO" not in data


def test_delete_var_missing_key_raises(tmp_path):
    vault_file = str(tmp_path / ".envault")
    with pytest.raises(KeyError):
        delete_var(PASSWORD, "MISSING", vault_file)
