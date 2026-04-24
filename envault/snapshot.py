"""Snapshot support: capture and restore point-in-time copies of the vault."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from envault.vault import load_vault, save_vault, VaultError


class SnapshotError(Exception):
    pass


def _get_snapshot_dir(vault_dir: str | None = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    snap_dir = base / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir


def _snapshot_name(label: str | None) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{label}" if label else ts


def create_snapshot(
    password: str,
    label: str | None = None,
    vault_dir: str | None = None,
) -> str:
    """Save a snapshot of the current vault. Returns the snapshot name."""
    data = load_vault(password, vault_dir=vault_dir)
    name = _snapshot_name(label)
    snap_dir = _get_snapshot_dir(vault_dir)
    snap_path = snap_dir / f"{name}.json"
    snap_path.write_text(json.dumps(data), encoding="utf-8")
    return name


def list_snapshots(vault_dir: str | None = None) -> list[str]:
    """Return snapshot names sorted oldest-first."""
    snap_dir = _get_snapshot_dir(vault_dir)
    names = sorted(p.stem for p in snap_dir.glob("*.json"))
    return names


def restore_snapshot(
    name: str,
    password: str,
    vault_dir: str | None = None,
) -> int:
    """Restore vault from a snapshot. Returns number of variables restored."""
    snap_dir = _get_snapshot_dir(vault_dir)
    snap_path = snap_dir / f"{name}.json"
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {name}")
    data = json.loads(snap_path.read_text(encoding="utf-8"))
    save_vault(data, password, vault_dir=vault_dir)
    return len(data)


def delete_snapshot(name: str, vault_dir: str | None = None) -> None:
    """Delete a named snapshot."""
    snap_dir = _get_snapshot_dir(vault_dir)
    snap_path = snap_dir / f"{name}.json"
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {name}")
    snap_path.unlink()
