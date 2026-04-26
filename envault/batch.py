"""Batch operations for envault — set, delete, or copy multiple variables at once."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import VaultError, load_vault, save_vault


class BatchError(Exception):
    """Raised when a batch operation fails."""


@dataclass
class BatchResult:
    """Summary of a completed batch operation."""

    succeeded: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)  # key -> error message

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)

    @property
    def ok(self) -> bool:
        """True when every operation in the batch succeeded."""
        return len(self.failed) == 0


def batch_set(
    variables: Dict[str, str],
    password: str,
    vault_dir: Optional[str] = None,
) -> BatchResult:
    """Set multiple variables in a single vault read/write cycle.

    Args:
        variables: Mapping of variable names to their values.
        password:  Vault encryption password.
        vault_dir: Optional override for the vault directory (used in tests).

    Returns:
        A :class:`BatchResult` describing which keys were written.
    """
    result = BatchResult()
    if not variables:
        return result

    try:
        data = load_vault(password, vault_dir=vault_dir)
    except VaultError as exc:
        raise BatchError(f"Could not load vault: {exc}") from exc

    for key, value in variables.items():
        try:
            _validate_key(key)
            data[key] = value
            result.succeeded.append(key)
        except ValueError as exc:
            result.failed[key] = str(exc)

    try:
        save_vault(data, password, vault_dir=vault_dir)
    except VaultError as exc:
        raise BatchError(f"Could not save vault: {exc}") from exc

    return result


def batch_delete(
    keys: List[str],
    password: str,
    vault_dir: Optional[str] = None,
) -> BatchResult:
    """Delete multiple variables in a single vault read/write cycle.

    Missing keys are recorded as failures but do not abort the operation.

    Args:
        keys:      List of variable names to remove.
        password:  Vault encryption password.
        vault_dir: Optional override for the vault directory.

    Returns:
        A :class:`BatchResult` describing which keys were removed.
    """
    result = BatchResult()
    if not keys:
        return result

    try:
        data = load_vault(password, vault_dir=vault_dir)
    except VaultError as exc:
        raise BatchError(f"Could not load vault: {exc}") from exc

    for key in keys:
        if key in data:
            del data[key]
            result.succeeded.append(key)
        else:
            result.failed[key] = "key not found"

    try:
        save_vault(data, password, vault_dir=vault_dir)
    except VaultError as exc:
        raise BatchError(f"Could not save vault: {exc}") from exc

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_key(key: str) -> None:
    """Raise ValueError if *key* is not a valid environment variable name."""
    if not key:
        raise ValueError("variable name must not be empty")
    if not key.replace("_", "").isalnum():
        raise ValueError(
            f"invalid variable name {key!r}: only letters, digits and underscores are allowed"
        )
    if key[0].isdigit():
        raise ValueError(f"invalid variable name {key!r}: must not start with a digit")
