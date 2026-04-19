"""Tests for envault.sync module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from envault.sync import push_vault, pull_vault, get_remote_config, save_remote_config, SyncError


REMOTE = "https://example.com"
TOKEN = "test-token-abc"


def test_push_vault_missing_file(tmp_path):
    with pytest.raises(SyncError, match="Vault file not found"):
        push_vault(str(tmp_path / "missing.vault"), REMOTE, TOKEN)


def test_push_vault_success(tmp_path):
    vault = tmp_path / "vault.enc"
    vault.write_bytes(b"encrypted-data")

    mock_resp = MagicMock()
    mock_resp.status = 204
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        push_vault(str(vault), REMOTE, TOKEN)  # should not raise


def test_push_vault_network_error(tmp_path):
    import urllib.error
    vault = tmp_path / "vault.enc"
    vault.write_bytes(b"data")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("conn refused")):
        with pytest.raises(SyncError, match="Failed to push vault"):
            push_vault(str(vault), REMOTE, TOKEN)


def test_pull_vault_writes_file(tmp_path):
    dest = tmp_path / "vault.enc"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"remote-encrypted"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        pull_vault(str(dest), REMOTE, TOKEN)

    assert dest.read_bytes() == b"remote-encrypted"


def test_pull_vault_network_error(tmp_path):
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        with pytest.raises(SyncError, match="Failed to pull vault"):
            pull_vault(str(tmp_path / "v.enc"), REMOTE, TOKEN)


def test_get_remote_config_missing(tmp_path):
    result = get_remote_config(str(tmp_path / "no.json"))
    assert result == {}


def test_save_and_get_remote_config_roundtrip(tmp_path):
    cfg_path = str(tmp_path / "remote.json")
    save_remote_config(cfg_path, REMOTE, TOKEN)
    cfg = get_remote_config(cfg_path)
    assert cfg["url"] == REMOTE
    assert cfg["token"] == TOKEN


def test_get_remote_config_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(SyncError, match="Invalid remote config JSON"):
        get_remote_config(str(bad))
