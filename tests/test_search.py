"""Tests for envault.search and envault.search_cli."""
import pytest
from unittest.mock import patch, MagicMock
from envault.search import search_vars, SearchError


VAULT_DATA = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "supersecret",
    "API_TOKEN": "token-abc123",
    "DEBUG": "true",
}


@pytest.fixture()
def mock_vault(tmp_path):
    with patch("envault.search.load_vault", return_value=dict(VAULT_DATA)):
        yield tmp_path


def test_search_matches_key(mock_vault):
    results = search_vars("password", "database", vault_dir=str(mock_vault))
    assert "DATABASE_URL" in results


def test_search_matches_value(mock_vault):
    results = search_vars("password", "postgres", vault_dir=str(mock_vault))
    assert "DATABASE_URL" in results


def test_search_keys_only_ignores_value(mock_vault):
    results = search_vars("password", "postgres", vault_dir=str(mock_vault), keys_only=True)
    assert results == {}


def test_search_keys_only_matches_key(mock_vault):
    results = search_vars("password", "api", vault_dir=str(mock_vault), keys_only=True)
    assert "API_TOKEN" in results


def test_search_case_insensitive(mock_vault):
    results = search_vars("password", "SECRET", vault_dir=str(mock_vault))
    assert "SECRET_KEY" in results


def test_search_no_matches_returns_empty(mock_vault):
    results = search_vars("password", "zzznomatch", vault_dir=str(mock_vault))
    assert results == {}


def test_search_empty_pattern_raises(mock_vault):
    with pytest.raises(SearchError):
        search_vars("password", "", vault_dir=str(mock_vault))


def test_search_multiple_matches(mock_vault):
    results = search_vars("password", "secret", vault_dir=str(mock_vault))
    # matches SECRET_KEY (key) and DATABASE_URL value contains 'supersecret'? no — 'secret' in 'supersecret'
    assert "SECRET_KEY" in results
