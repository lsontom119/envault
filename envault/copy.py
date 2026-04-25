"""Copy or rename environment variables within the vault."""

from envault.vault import load_vault, save_vault, VaultError


class CopyError(Exception):
    pass


def copy_var(src_key: str, dst_key: str, password: str, vault_dir: str = None, overwrite: bool = False) -> None:
    """Copy the value of src_key to dst_key in the vault."""
    data = load_vault(password, vault_dir=vault_dir)

    if src_key not in data:
        raise CopyError(f"Source key '{src_key}' not found in vault.")

    if dst_key in data and not overwrite:
        raise CopyError(
            f"Destination key '{dst_key}' already exists. Use --overwrite to replace it."
        )

    data[dst_key] = data[src_key]
    save_vault(data, password, vault_dir=vault_dir)


def rename_var(src_key: str, dst_key: str, password: str, vault_dir: str = None, overwrite: bool = False) -> None:
    """Rename src_key to dst_key in the vault (copy then delete original)."""
    data = load_vault(password, vault_dir=vault_dir)

    if src_key not in data:
        raise CopyError(f"Source key '{src_key}' not found in vault.")

    if dst_key in data and not overwrite:
        raise CopyError(
            f"Destination key '{dst_key}' already exists. Use --overwrite to replace it."
        )

    data[dst_key] = data[src_key]
    del data[src_key]
    save_vault(data, password, vault_dir=vault_dir)
