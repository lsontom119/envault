"""Remote sync support for envault vaults via a simple HTTP backend."""

import json
import urllib.request
import urllib.error
from typing import Optional


class SyncError(Exception):
    pass


def push_vault(vault_path: str, remote_url: str, token: str) -> None:
    """Push encrypted vault bytes to a remote endpoint."""
    try:
        with open(vault_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        raise SyncError(f"Vault file not found: {vault_path}")

    req = urllib.request.Request(
        f"{remote_url.rstrip('/')}/vault",
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 204):
                raise SyncError(f"Unexpected status from remote: {resp.status}")
    except urllib.error.URLError as e:
        raise SyncError(f"Failed to push vault: {e}") from e


def pull_vault(vault_path: str, remote_url: str, token: str) -> None:
    """Pull encrypted vault bytes from a remote endpoint and write locally."""
    req = urllib.request.Request(
        f"{remote_url.rstrip('/')}/vault",
        method="GET",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
    except urllib.error.URLError as e:
        raise SyncError(f"Failed to pull vault: {e}") from e

    with open(vault_path, "wb") as f:
        f.write(data)


def get_remote_config(config_path: str) -> dict:
    """Load remote config (url + token) from a JSON file."""
    try:
        with open(config_path) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SyncError(f"Invalid remote config JSON: {e}") from e
    return cfg


def save_remote_config(config_path: str, url: str, token: str) -> None:
    """Persist remote URL and token to a JSON config file."""
    with open(config_path, "w") as f:
        json.dump({"url": url, "token": token}, f, indent=2)
