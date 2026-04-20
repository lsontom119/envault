"""Search and filter vault variables."""
from typing import Optional
from envault.vault import load_vault


class SearchError(Exception):
    pass


def search_vars(
    password: str,
    pattern: str,
    vault_dir: Optional[str] = None,
    keys_only: bool = False,
) -> dict:
    """Return vault entries whose key or value matches *pattern*.

    Args:
        password: Vault password.
        pattern: Case-insensitive substring to search for.
        vault_dir: Override vault directory (for testing).
        keys_only: When True, only search keys, not values.

    Returns:
        Dict of matching key/value pairs.
    """
    if not pattern:
        raise SearchError("Search pattern must not be empty.")

    data = load_vault(password, vault_dir=vault_dir)
    needle = pattern.lower()
    results = {}
    for key, value in data.items():
        if needle in key.lower():
            results[key] = value
        elif not keys_only and needle in value.lower():
            results[key] = value
    return results
