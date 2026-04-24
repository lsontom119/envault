"""Tests for envault.tags module."""
from __future__ import annotations

import os
import pytest

from envault.tags import TagError, add_tag, list_tags, remove_tag, vars_with_tag
from envault.vault import save_vault

PASSWORD = "test-password"


@pytest.fixture()
def vault_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    initial = {"DB_URL": "postgres://localhost/db", "API_KEY": "secret123"}
    save_vault(initial, PASSWORD, vault_dir=str(tmp_path))
    return tmp_path


def test_add_tag_success(vault_env):
    add_tag(PASSWORD, "DB_URL", "database", vault_dir=str(vault_env))
    tags = list_tags(PASSWORD, var_name="DB_URL", vault_dir=str(vault_env))
    assert "database" in tags["DB_URL"]


def test_add_tag_idempotent(vault_env):
    add_tag(PASSWORD, "DB_URL", "infra", vault_dir=str(vault_env))
    add_tag(PASSWORD, "DB_URL", "infra", vault_dir=str(vault_env))
    tags = list_tags(PASSWORD, var_name="DB_URL", vault_dir=str(vault_env))
    assert tags["DB_URL"].count("infra") == 1


def test_add_tag_missing_variable_raises(vault_env):
    with pytest.raises(TagError, match="not found"):
        add_tag(PASSWORD, "NONEXISTENT", "mytag", vault_dir=str(vault_env))


def test_remove_tag_success(vault_env):
    add_tag(PASSWORD, "API_KEY", "sensitive", vault_dir=str(vault_env))
    remove_tag(PASSWORD, "API_KEY", "sensitive", vault_dir=str(vault_env))
    tags = list_tags(PASSWORD, var_name="API_KEY", vault_dir=str(vault_env))
    assert "sensitive" not in tags.get("API_KEY", [])


def test_remove_tag_not_present_raises(vault_env):
    with pytest.raises(TagError, match="not found"):
        remove_tag(PASSWORD, "DB_URL", "ghost", vault_dir=str(vault_env))


def test_list_tags_all(vault_env):
    add_tag(PASSWORD, "DB_URL", "database", vault_dir=str(vault_env))
    add_tag(PASSWORD, "API_KEY", "sensitive", vault_dir=str(vault_env))
    tags = list_tags(PASSWORD, vault_dir=str(vault_env))
    assert "DB_URL" in tags
    assert "API_KEY" in tags


def test_list_tags_empty_when_none_set(vault_env):
    tags = list_tags(PASSWORD, vault_dir=str(vault_env))
    assert tags == {}


def test_vars_with_tag(vault_env):
    add_tag(PASSWORD, "DB_URL", "infra", vault_dir=str(vault_env))
    add_tag(PASSWORD, "API_KEY", "infra", vault_dir=str(vault_env))
    result = vars_with_tag(PASSWORD, "infra", vault_dir=str(vault_env))
    assert set(result) == {"DB_URL", "API_KEY"}


def test_vars_with_tag_returns_empty_for_unknown_tag(vault_env):
    result = vars_with_tag(PASSWORD, "nonexistent-tag", vault_dir=str(vault_env))
    assert result == []
