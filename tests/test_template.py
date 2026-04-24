"""Tests for envault.template module."""

import pytest

from envault.template import TemplateError, list_placeholders, render_file, render_string


# ---------------------------------------------------------------------------
# render_string
# ---------------------------------------------------------------------------

def test_render_string_basic():
    result = render_string("Hello, {{ NAME }}!", {"NAME": "Alice"})
    assert result == "Hello, Alice!"


def test_render_string_multiple_placeholders():
    tmpl = "{{ GREETING }}, {{ NAME }}! You are {{ AGE }} years old."
    result = render_string(tmpl, {"GREETING": "Hi", "NAME": "Bob", "AGE": "30"})
    assert result == "Hi, Bob! You are 30 years old."


def test_render_string_repeated_placeholder():
    result = render_string("{{ X }} and {{ X }}", {"X": "foo"})
    assert result == "foo and foo"


def test_render_string_strict_raises_on_missing():
    with pytest.raises(TemplateError, match="undefined variable"):
        render_string("{{ MISSING }}", {}, strict=True)


def test_render_string_non_strict_leaves_unknown():
    result = render_string("{{ MISSING }}", {}, strict=False)
    assert "{{ MISSING }}" in result


def test_render_string_no_placeholders():
    result = render_string("plain text", {"X": "y"})
    assert result == "plain text"


def test_render_string_whitespace_inside_braces():
    result = render_string("{{  KEY  }}", {"KEY": "value"})
    assert result == "value"


# ---------------------------------------------------------------------------
# render_file
# ---------------------------------------------------------------------------

def test_render_file_success(tmp_path):
    tmpl = tmp_path / "app.env.tmpl"
    tmpl.write_text("DB_URL={{ DB_URL }}\nSECRET={{ SECRET }}\n")
    result = render_file(str(tmpl), {"DB_URL": "postgres://localhost/db", "SECRET": "s3cr3t"})
    assert "postgres://localhost/db" in result
    assert "s3cr3t" in result


def test_render_file_missing_file_raises():
    with pytest.raises(TemplateError, match="Cannot read template file"):
        render_file("/nonexistent/path/file.tmpl", {})


def test_render_file_strict_raises_on_missing(tmp_path):
    tmpl = tmp_path / "t.tmpl"
    tmpl.write_text("{{ UNDEFINED }}")
    with pytest.raises(TemplateError, match="UNDEFINED"):
        render_file(str(tmpl), {}, strict=True)


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------

def test_list_placeholders_returns_sorted_unique():
    tmpl = "{{ B }} {{ A }} {{ B }} {{ C }}"
    assert list_placeholders(tmpl) == ["A", "B", "C"]


def test_list_placeholders_empty_when_none():
    assert list_placeholders("no placeholders here") == []
