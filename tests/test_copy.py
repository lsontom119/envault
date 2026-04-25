"""Tests for envault.copy (copy_var and rename_var)."""

import os
import pytest

from envault.vault import save_vault, load_vault
from envault.copy import copy_var, rename_var, CopyError

PASSWORD = "test-password"


@pytest.fixture
def vault_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    data = {"API_KEY": "secret123", "DB_HOST": "localhost"}
    save_vault(data, PASSWORD, vault_dir=str(tmp_path))
    return tmp_path


def test_copy_var_creates_new_key(vault_env):
    copy_var("API_KEY", "API_KEY_BACKUP", PASSWORD, vault_dir=str(vault_env))
    data = load_vault(PASSWORD, vault_dir=str(vault_env))
    assert data["API_KEY_BACKUP"] == "secret123"
    assert data["API_KEY"] == "secret123"  # original preserved


def test_copy_var_preserves_original(vault_env):
    copy_var("DB_HOST", "DB_HOST_COPY", PASSWORD, vault_dir=str(vault_env))
    data = load_vault(PASSWORD, vault_dir=str(vault_env))
    assert "DB_HOST" in data


def test_copy_var_missing_source_raises(vault_env):
    with pytest.raises(CopyError, match="Source key 'MISSING' not found"):
        copy_var("MISSING", "NEW_KEY", PASSWORD, vault_dir=str(vault_env))


def test_copy_var_existing_dst_raises_without_overwrite(vault_env):
    with pytest.raises(CopyError, match="already exists"):
        copy_var("API_KEY", "DB_HOST", PASSWORD, vault_dir=str(vault_env))


def test_copy_var_existing_dst_succeeds_with_overwrite(vault_env):
    copy_var("API_KEY", "DB_HOST", PASSWORD, vault_dir=str(vault_env), overwrite=True)
    data = load_vault(PASSWORD, vault_dir=str(vault_env))
    assert data["DB_HOST"] == "secret123"


def test_rename_var_removes_source(vault_env):
    rename_var("API_KEY", "API_KEY_NEW", PASSWORD, vault_dir=str(vault_env))
    data = load_vault(PASSWORD, vault_dir=str(vault_env))
    assert "API_KEY" not in data
    assert data["API_KEY_NEW"] == "secret123"


def test_rename_var_missing_source_raises(vault_env):
    with pytest.raises(CopyError, match="Source key 'NOPE' not found"):
        rename_var("NOPE", "SOMETHING", PASSWORD, vault_dir=str(vault_env))


def test_rename_var_existing_dst_raises_without_overwrite(vault_env):
    with pytest.raises(CopyError, match="already exists"):
        rename_var("API_KEY", "DB_HOST", PASSWORD, vault_dir=str(vault_env))


def test_rename_var_existing_dst_succeeds_with_overwrite(vault_env):
    rename_var("API_KEY", "DB_HOST", PASSWORD, vault_dir=str(vault_env), overwrite=True)
    data = load_vault(PASSWORD, vault_dir=str(vault_env))
    assert "API_KEY" not in data
    assert data["DB_HOST"] == "secret123"
