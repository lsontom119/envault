"""Tests for envault.snapshot_cli."""

from __future__ import annotations

import argparse
import pytest

from envault.snapshot_cli import register_snapshot_commands
from envault.vault import save_vault


PASSWORD = "cli-test-password"


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    register_snapshot_commands(sub)
    return p


@pytest.fixture()
def vault_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    save_vault({"FOO": "bar"}, PASSWORD, vault_dir=str(tmp_path))
    return str(tmp_path)


def test_parser_snapshot_create(parser):
    args = parser.parse_args(["snapshot", "create"])
    assert args.snapshot_cmd == "create"


def test_parser_snapshot_create_with_label(parser):
    args = parser.parse_args(["snapshot", "create", "--label", "v1"])
    assert args.label == "v1"


def test_parser_snapshot_list(parser):
    args = parser.parse_args(["snapshot", "list"])
    assert args.snapshot_cmd == "list"


def test_parser_snapshot_restore(parser):
    args = parser.parse_args(["snapshot", "restore", "20240101T000000Z_v1"])
    assert args.name == "20240101T000000Z_v1"


def test_parser_snapshot_delete(parser):
    args = parser.parse_args(["snapshot", "delete", "20240101T000000Z_v1"])
    assert args.name == "20240101T000000Z_v1"


def test_cmd_snapshot_list_no_snapshots(parser, vault_env, capsys, monkeypatch):
    from envault import snapshot_cli
    monkeypatch.setattr(snapshot_cli, "list_snapshots", lambda: [])
    args = parser.parse_args(["snapshot", "list"])
    args.func(args)
    captured = capsys.readouterr()
    assert "No snapshots" in captured.out


def test_cmd_snapshot_create_prints_name(parser, vault_env, capsys, monkeypatch):
    from envault import snapshot_cli
    monkeypatch.setattr(snapshot_cli, "_get_password", lambda: PASSWORD)
    monkeypatch.setattr(snapshot_cli, "create_snapshot", lambda pw, label=None: "20240601T120000Z_test")
    args = parser.parse_args(["snapshot", "create", "--label", "test"])
    args.func(args)
    captured = capsys.readouterr()
    assert "20240601T120000Z_test" in captured.out


def test_cmd_snapshot_restore_prints_count(parser, vault_env, capsys, monkeypatch):
    from envault import snapshot_cli
    monkeypatch.setattr(snapshot_cli, "_get_password", lambda: PASSWORD)
    monkeypatch.setattr(snapshot_cli, "restore_snapshot", lambda name, pw: 3)
    args = parser.parse_args(["snapshot", "restore", "some-snap"])
    args.func(args)
    captured = capsys.readouterr()
    assert "3" in captured.out
    assert "some-snap" in captured.out
