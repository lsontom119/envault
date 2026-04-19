"""Tests for sync-related CLI commands (push, pull, remote add)."""

import pytest
from unittest.mock import patch, MagicMock
from envault.cli import build_parser, cmd_push, cmd_pull, cmd_remote_add


@pytest.fixture
def parser():
    return build_parser()


def test_parser_remote_add(parser):
    args = parser.parse_args(["remote", "add", "https://example.com", "tok123"])
    assert args.url == "https://example.com"
    assert args.token == "tok123"


def test_parser_push(parser):
    args = parser.parse_args(["push"])
    assert args.command == "push"


def test_parser_pull(parser):
    args = parser.parse_args(["pull"])
    assert args.command == "pull"


def test_cmd_remote_add_saves_config(tmp_path):
    args = MagicMock()
    args.url = "https://sync.example.com"
    args.token = "mytoken"

    with patch("envault.cli.get_remote_config_path", return_value=str(tmp_path / "remote.json")), \
         patch("envault.cli.save_remote_config") as mock_save:
        cmd_remote_add(args)
        mock_save.assert_called_once_with(str(tmp_path / "remote.json"), args.url, args.token)


def test_cmd_push_no_remote_exits(tmp_path, capsys):
    args = MagicMock()
    with patch("envault.cli.get_remote_config_path", return_value=str(tmp_path / "r.json")), \
         patch("envault.cli.get_remote_config", return_value={}):
        with pytest.raises(SystemExit) as exc:
            cmd_push(args)
        assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "No remote configured" in captured.err


def test_cmd_push_success(tmp_path):
    args = MagicMock()
    cfg = {"url": "https://example.com", "token": "tok"}
    with patch("envault.cli.get_remote_config_path", return_value=str(tmp_path / "r.json")), \
         patch("envault.cli.get_remote_config", return_value=cfg), \
         patch("envault.vault._get_vault_path", return_value=str(tmp_path / "v.enc")), \
         patch("envault.cli.push_vault") as mock_push:
        cmd_push(args)
        mock_push.assert_called_once()


def test_cmd_pull_success(tmp_path):
    args = MagicMock()
    cfg = {"url": "https://example.com", "token": "tok"}
    with patch("envault.cli.get_remote_config_path", return_value=str(tmp_path / "r.json")), \
         patch("envault.cli.get_remote_config", return_value=cfg), \
         patch("envault.vault._get_vault_path", return_value=str(tmp_path / "v.enc")), \
         patch("envault.cli.pull_vault") as mock_pull:
        cmd_pull(args)
        mock_pull.assert_called_once()
