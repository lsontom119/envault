"""Tests for envault.rotate."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.rotate import RotateError, rotate_password
from envault.vault import load_vault, save_vault


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_vault(vault_dir: Path, password: str, data: dict) -> None:
    save_vault(data, password, vault_dir=vault_dir)


def test_rotate_changes_password(vault_dir: Path) -> None:
    _make_vault(vault_dir, "old-pass", {"KEY": "value"})
    count = rotate_password("old-pass", "new-pass", vault_dir=vault_dir)
    assert count == 1
    # Old password should no longer work
    from envault.vault import VaultError
    with pytest.raises(VaultError):
        load_vault("old-pass", vault_dir=vault_dir)


def test_rotate_new_password_decrypts(vault_dir: Path) -> None:
    _make_vault(vault_dir, "old-pass", {"A": "1", "B": "2"})
    rotate_password("old-pass", "new-pass", vault_dir=vault_dir)
    data = load_vault("new-pass", vault_dir=vault_dir)
    assert data == {"A": "1", "B": "2"}


def test_rotate_returns_variable_count(vault_dir: Path) -> None:
    _make_vault(vault_dir, "pw", {"X": "1", "Y": "2", "Z": "3"})
    count = rotate_password("pw", "new-pw", vault_dir=vault_dir)
    assert count == 3


def test_rotate_missing_vault_raises(vault_dir: Path) -> None:
    with pytest.raises(RotateError, match="No vault found"):
        rotate_password("any", "other", vault_dir=vault_dir)


def test_rotate_wrong_old_password_raises(vault_dir: Path) -> None:
    _make_vault(vault_dir, "correct", {"K": "v"})
    with pytest.raises(RotateError, match="Could not decrypt"):
        rotate_password("wrong", "new-pass", vault_dir=vault_dir)


def test_rotate_empty_vault(vault_dir: Path) -> None:
    _make_vault(vault_dir, "pw", {})
    count = rotate_password("pw", "new-pw", vault_dir=vault_dir)
    assert count == 0
    data = load_vault("new-pw", vault_dir=vault_dir)
    assert data == {}
