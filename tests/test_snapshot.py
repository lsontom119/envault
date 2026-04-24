"""Tests for envault.snapshot."""

from __future__ import annotations

import json
import pytest

from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envault.vault import save_vault, load_vault


PASSWORD = "test-password-123"


@pytest.fixture()
def vault_env(tmp_path, monkeypatch):
    """Provide an isolated vault + snapshot directory."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    vault_dir = str(tmp_path)
    initial = {"API_KEY": "abc123", "DEBUG": "true"}
    save_vault(initial, PASSWORD, vault_dir=vault_dir)
    return vault_dir


def test_create_snapshot_returns_name(vault_env):
    name = create_snapshot(PASSWORD, vault_dir=vault_env)
    assert isinstance(name, str)
    assert len(name) > 0


def test_create_snapshot_with_label(vault_env):
    name = create_snapshot(PASSWORD, label="before-deploy", vault_dir=vault_env)
    assert "before-deploy" in name


def test_list_snapshots_empty(tmp_path):
    names = list_snapshots(vault_dir=str(tmp_path))
    assert names == []


def test_list_snapshots_returns_created(vault_env):
    create_snapshot(PASSWORD, label="snap1", vault_dir=vault_env)
    create_snapshot(PASSWORD, label="snap2", vault_dir=vault_env)
    names = list_snapshots(vault_dir=vault_env)
    assert len(names) == 2
    assert all("snap" in n for n in names)


def test_restore_snapshot_recovers_data(vault_env):
    name = create_snapshot(PASSWORD, vault_dir=vault_env)
    # Overwrite vault with new data
    save_vault({"NEW_KEY": "new_val"}, PASSWORD, vault_dir=vault_env)
    count = restore_snapshot(name, PASSWORD, vault_dir=vault_env)
    assert count == 2  # original had 2 keys
    restored = load_vault(PASSWORD, vault_dir=vault_env)
    assert restored["API_KEY"] == "abc123"
    assert "NEW_KEY" not in restored


def test_restore_nonexistent_snapshot_raises(vault_env):
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("ghost-snapshot", PASSWORD, vault_dir=vault_env)


def test_delete_snapshot_removes_it(vault_env):
    name = create_snapshot(PASSWORD, label="to-delete", vault_dir=vault_env)
    assert name in list_snapshots(vault_dir=vault_env)
    delete_snapshot(name, vault_dir=vault_env)
    assert name not in list_snapshots(vault_dir=vault_env)


def test_delete_nonexistent_snapshot_raises(vault_env):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot("no-such-snapshot", vault_dir=vault_env)


def test_list_snapshots_sorted(vault_env):
    names = []
    for label in ("a", "b", "c"):
        names.append(create_snapshot(PASSWORD, label=label, vault_dir=vault_env))
    listed = list_snapshots(vault_dir=vault_env)
    assert listed == sorted(listed)
