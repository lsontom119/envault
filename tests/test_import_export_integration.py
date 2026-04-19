"""Integration tests for import/export round-trip using file_utils."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.file_utils import write_dotenv_file, read_dotenv_file
from envault.import_export_cli import cmd_import, cmd_export_file
from unittest.mock import MagicMock


@pytest.fixture
def vault_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_import_then_export_roundtrip(vault_env):
    """Variables imported from a .env file can be exported back identically."""
    original = {"SERVICE_URL": "https://example.com", "TOKEN": "abc123"}
    env_in = vault_env / "input.env"
    write_dotenv_file(env_in, original)

    import_args = MagicMock()
    import_args.file = str(env_in)

    stored = {}

    def fake_set(key, value, password):
        stored[key] = value

    with patch("envault.import_export_cli._get_password", return_value="pw"), \
         patch("envault.import_export_cli.set_var", side_effect=fake_set), \
         patch("envault.import_export_cli.record_event"):
        cmd_import(import_args)

    assert stored == original

    out_path = vault_env / "output.env"
    export_args = MagicMock()
    export_args.format = "dotenv"
    export_args.output = str(out_path)

    with patch("envault.import_export_cli._get_password", return_value="pw"), \
         patch("envault.import_export_cli.load_vault", return_value=stored), \
         patch("envault.import_export_cli.record_event"):
        cmd_export_file(export_args)

    result = read_dotenv_file(out_path)
    assert result == original
