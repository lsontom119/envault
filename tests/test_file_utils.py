"""Tests for envault.file_utils."""

import pytest
from pathlib import Path
from envault.file_utils import parse_dotenv, read_dotenv_file, write_dotenv_file, merge_dotenv


def test_parse_dotenv_basic():
    text = "FOO=bar\nBAZ=qux\n"
    result = parse_dotenv(text)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_skips_comments():
    text = "# comment\nKEY=value\n"
    assert "KEY" in parse_dotenv(text)
    assert len(parse_dotenv(text)) == 1


def test_parse_dotenv_skips_blank_lines():
    text = "\n\nA=1\n\n"
    assert parse_dotenv(text) == {"A": "1"}


def test_parse_dotenv_strips_double_quotes():
    text = 'KEY="hello world"'
    assert parse_dotenv(text)["KEY"] == "hello world"


def test_parse_dotenv_strips_single_quotes():
    text = "KEY='hello'"
    assert parse_dotenv(text)["KEY"] == "hello"


def test_parse_dotenv_skips_invalid_lines():
    text = "NOTANASSIGNMENT\nGOOD=yes"
    result = parse_dotenv(text)
    assert "NOTANASSIGNMENT" not in result
    assert result["GOOD"] == "yes"


def test_write_and_read_dotenv_roundtrip(tmp_path):
    data = {"ALPHA": "one", "BETA": "two"}
    p = tmp_path / ".env"
    write_dotenv_file(p, data)
    result = read_dotenv_file(p)
    assert result == data


def test_write_dotenv_escapes_quotes(tmp_path):
    data = {"MSG": 'say "hello"'}
    p = tmp_path / ".env"
    write_dotenv_file(p, data)
    content = p.read_text()
    assert '\\"' in content


def test_merge_dotenv_override():
    base = {"A": "1", "B": "2"}
    override = {"B": "99", "C": "3"}
    merged = merge_dotenv(base, override)
    assert merged == {"A": "1", "B": "99", "C": "3"}


def test_merge_dotenv_does_not_mutate_base():
    base = {"X": "orig"}
    merge_dotenv(base, {"X": "new"})
    assert base["X"] == "orig"
