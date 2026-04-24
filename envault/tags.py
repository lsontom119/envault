"""Tag management for vault variables."""
from __future__ import annotations

from typing import Dict, List

from envault.vault import VaultError, load_vault, save_vault


class TagError(Exception):
    pass


_TAGS_KEY = "__tags__"


def _get_tags(vault_data: dict) -> Dict[str, List[str]]:
    """Return the tags mapping stored inside vault data."""
    return vault_data.get(_TAGS_KEY, {})


def add_tag(password: str, var_name: str, tag: str, vault_dir: str | None = None) -> None:
    """Add *tag* to *var_name*. Raises TagError if the variable does not exist."""
    data = load_vault(password, vault_dir=vault_dir)
    if var_name not in data:
        raise TagError(f"Variable '{var_name}' not found in vault.")
    tags: Dict[str, List[str]] = data.get(_TAGS_KEY, {})
    current = tags.get(var_name, [])
    if tag not in current:
        current.append(tag)
    tags[var_name] = current
    data[_TAGS_KEY] = tags
    save_vault(data, password, vault_dir=vault_dir)


def remove_tag(password: str, var_name: str, tag: str, vault_dir: str | None = None) -> None:
    """Remove *tag* from *var_name*. Raises TagError if tag is not present."""
    data = load_vault(password, vault_dir=vault_dir)
    tags: Dict[str, List[str]] = data.get(_TAGS_KEY, {})
    current = tags.get(var_name, [])
    if tag not in current:
        raise TagError(f"Tag '{tag}' not found on variable '{var_name}'.")
    current.remove(tag)
    tags[var_name] = current
    data[_TAGS_KEY] = tags
    save_vault(data, password, vault_dir=vault_dir)


def list_tags(password: str, var_name: str | None = None, vault_dir: str | None = None) -> Dict[str, List[str]]:
    """Return tags for *var_name*, or all tags if *var_name* is None."""
    data = load_vault(password, vault_dir=vault_dir)
    tags = _get_tags(data)
    if var_name is not None:
        return {var_name: tags.get(var_name, [])}
    return {k: v for k, v in tags.items() if v}


def vars_with_tag(password: str, tag: str, vault_dir: str | None = None) -> List[str]:
    """Return variable names that carry *tag*."""
    data = load_vault(password, vault_dir=vault_dir)
    tags = _get_tags(data)
    return [var for var, tag_list in tags.items() if tag in tag_list]
