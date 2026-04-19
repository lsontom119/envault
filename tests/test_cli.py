"""Tests for the CLI layer."""

import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from envault.cli import build_parser, cmd_set, cmd_get, cmd_export
from envault.vault import VaultError


PASSWORD = "cli-test-pass"


@pytest.fixture
def parser():
    return build_parser()


def test_parser_set_command(parser):
    args = parser.parse_args(["set", "MY_KEY", "my_value"])
    assert args.command == "set"
    assert args.key == "MY_KEY"
    assert args.value == "my_value"


def test_parser_get_command(parser):
    args = parser.parse_args(["get", "MY_KEY"])
    assert args.command == "get"
    assert args.key == "MY_KEY"


def test_parser_export_default_format(parser):
    args = parser.parse_args(["export"])
    assert args.format == "shell"


def test_parser_export_dotenv_format(parser):
    args = parser.parse_args(["export", "--format", "dotenv"])
    assert args.format == "dotenv"


def test_cmd_set_success(capsys):
    args = Namespace(key="FOO", value="bar")
    with patch("envault.cli.getpass", return_value=PASSWORD), \
         patch("envault.cli.set_var") as mock_set:
        cmd_set(args)
        mock_set.assert_called_once_with("FOO", "bar", PASSWORD)
    captured = capsys.readouterr()
    assert "FOO" in captured.out


def test_cmd_set_vault_error_exits(capsys):
    args = Namespace(key="FOO", value="bar")
    with patch("envault.cli.getpass", return_value=PASSWORD), \
         patch("envault.cli.set_var", side_effect=VaultError("bad")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_set(args)
    assert exc_info.value.code == 1


def test_cmd_get_success(capsys):
    args = Namespace(key="FOO")
    with patch("envault.cli.getpass", return_value=PASSWORD), \
         patch("envault.cli.get_var", return_value="bar"):
        cmd_get(args)
    captured = capsys.readouterr()
    assert "bar" in captured.out


def test_cmd_get_missing_key_exits(capsys):
    args = Namespace(key="MISSING")
    with patch("envault.cli.getpass", return_value=PASSWORD), \
         patch("envault.cli.get_var", return_value=None), \
         pytest.raises(SystemExit) as exc_info:
        cmd_get(args)
    assert exc_info.value.code == 1


def test_cmd_export_dotenv(capsys):
    args = Namespace(format="dotenv")
    fake_data = {"A": "1", "B": "2"}
    with patch("envault.cli.getpass", return_value=PASSWORD), \
         patch("envault.cli.load_vault", return_value=fake_data):
        cmd_export(args)
    captured = capsys.readouterr()
    assert "A=" in captured.out
