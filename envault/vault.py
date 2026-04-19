"""Vault file read/write operations for envault."""

import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import decrypt, encrypt

DEFAULT_VAULT_FILE = ".envault"


class VaultError(Exception):
    pass


def _get_vault_path(vault_file: str = DEFAULT_VAULT_FILE) -> Path:
    return Path(vault_file)


def load_vault(password: str, vault_file: str = DEFAULT_VAULT_FILE) -> Dict[str, str]:
    """Load and decrypt the vault, returning a dict of env vars."""
    path = _get_vault_path(vault_file)
    if not path.exists():
        return {}
    try:
        ciphertext = path.read_bytes()
        plaintext = decrypt(password, ciphertext)
        return json.loads(plaintext)
    except Exception as e:
        raise VaultError(f"Failed to load vault: {e}") from e


def save_vault(
    password: str,
    data: Dict[str, str],
    vault_file: str = DEFAULT_VAULT_FILE,
) -> None:
    """Encrypt and save the vault to disk."""
    path = _get_vault_path(vault_file)
    try:
        plaintext = json.dumps(data).encode()
        ciphertext = encrypt(password, plaintext)
        path.write_bytes(ciphertext)
    except Exception as e:
        raise VaultError(f"Failed to save vault: {e}") from e


def set_var(password: str, key: str, value: str, vault_file: str = DEFAULT_VAULT_FILE) -> None:
    """Set a single environment variable in the vault."""
    data = load_vault(password, vault_file)
    data[key] = value
    save_vault(password, data, vault_file)


def delete_var(password: str, key: str, vault_file: str = DEFAULT_VAULT_FILE) -> None:
    """Delete a variable from the vault. Raises KeyError if not found."""
    data = load_vault(password, vault_file)
    if key not in data:
        raise KeyError(f"Variable '{key}' not found in vault.")
    del data[key]
    save_vault(password, data, vault_file)
