"""Key rotation: re-encrypt vault with a new password."""

from __future__ import annotations

from pathlib import Path

from envault.vault import VaultError, _get_vault_path, load_vault, save_vault
from envault.audit import record_event


class RotateError(Exception):
    """Raised when key rotation fails."""


def rotate_password(
    old_password: str,
    new_password: str,
    vault_dir: Path | None = None,
) -> int:
    """Re-encrypt the vault with *new_password*.

    Returns the number of variables that were migrated.

    Raises
    ------
    RotateError
        If the vault cannot be read with *old_password* or written with
        *new_password*.
    """
    vault_path = _get_vault_path(vault_dir)

    if not vault_path.exists():
        raise RotateError("No vault found. Nothing to rotate.")

    try:
        data = load_vault(old_password, vault_dir=vault_dir)
    except VaultError as exc:
        raise RotateError(f"Could not decrypt vault with old password: {exc}") from exc

    try:
        save_vault(data, new_password, vault_dir=vault_dir)
    except Exception as exc:  # pragma: no cover
        raise RotateError(f"Could not save vault with new password: {exc}") from exc

    record_event("rotate", key=None)
    return len(data)
