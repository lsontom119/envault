"""Tests for import/export CLI commands."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envault.import_export_cli import cmd_import, cmd_export_file, register_import_export_commands
import argparse


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_import_export_commands(sub)
    return p


@pytest.fixture
def dotenv_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n# comment\n\nINVALID\n")
    return f


def test_parser_import(parser):
    args = parser.parse_args(["import", "myfile.env"])
    assert args.file == "myfile.env"
    assert args.func == cmd_import


def test_parser_export_file_defaults(parser):
    args = parser.parse_args(["export-file"])
    assert args.format == "dotenv"
    assert args.output is None


def test_parser_export_file_shell(parser):
    args = parser.parse_args(["export-file", "--format", "shell", "--output", "vars.sh"])
    assert args.format == "shell"
    assert args.output == "vars.sh"


def test_cmd_import_reads_vars(dotenv_file, tmp_path):
    args = MagicMock()
    args.file = str(dotenv_file)
    with patch("envault.import_export_cli._get_password", return_value="secret"), \
         patch("envault.import_export_cli.set_var") as mock_set, \
         patch("envault.import_export_cli.record_event"):
        cmd_import(args)
    calls = {c.args[0] for c in mock_set.call_args_list}
    assert "FOO" in calls
    assert "BAZ" in calls
    assert len(mock_set.call_args_list) == 2


def test_cmd_import_missing_file(tmp_path):
    args = MagicMock()
    args.file = str(tmp_path / "nonexistent.env")
    with patch("envault.import_export_cli._get_password", return_value="secret"):
        with pytest.raises(SystemExit):
            cmd_import(args)


def test_cmd_export_file_dotenv(tmp_path):
    args = MagicMock()
    args.format = "dotenv"
    args.output = str(tmp_path / "out.env")
    with patch("envault.import_export_cli._get_password", return_value="secret"), \
         patch("envault.import_export_cli.load_vault", return_value={"KEY": "val"}), \
         patch("envault.import_export_cli.record_event"):
        cmd_export_file(args)
    content = Path(args.output).read_text()
    assert "KEY" in content


def test_cmd_export_file_shell(tmp_path):
    args = MagicMock()
    args.format = "shell"
    args.output = str(tmp_path / "vars.sh")
    with patch("envault.import_export_cli._get_password", return_value="secret"), \
         patch("envault.import_export_cli.load_vault", return_value={"X": "1"}), \
         patch("envault.import_export_cli.record_event"):
        cmd_export_file(args)
    content = Path(args.output).read_text()
    assert "#!/" in content
