"""CLI commands for vault snapshots."""

from __future__ import annotations

import argparse
import sys

from envault.cli import _get_password
from envault.snapshot import SnapshotError, create_snapshot, delete_snapshot, list_snapshots, restore_snapshot


def cmd_snapshot_create(args: argparse.Namespace) -> None:
    password = _get_password()
    try:
        name = create_snapshot(password, label=args.label or None)
        print(f"Snapshot created: {name}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_list(args: argparse.Namespace) -> None:
    names = list_snapshots()
    if not names:
        print("No snapshots found.")
        return
    for name in names:
        print(name)


def cmd_snapshot_restore(args: argparse.Namespace) -> None:
    password = _get_password()
    try:
        count = restore_snapshot(args.name, password)
        print(f"Restored {count} variable(s) from snapshot '{args.name}'.")
    except SnapshotError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_delete(args: argparse.Namespace) -> None:
    try:
        delete_snapshot(args.name)
        print(f"Snapshot '{args.name}' deleted.")
    except SnapshotError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_snapshot_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    snap = subparsers.add_parser("snapshot", help="Manage vault snapshots")
    snap_sub = snap.add_subparsers(dest="snapshot_cmd", required=True)

    # create
    p_create = snap_sub.add_parser("create", help="Create a snapshot")
    p_create.add_argument("--label", default="", help="Optional label for the snapshot")
    p_create.set_defaults(func=cmd_snapshot_create)

    # list
    p_list = snap_sub.add_parser("list", help="List all snapshots")
    p_list.set_defaults(func=cmd_snapshot_list)

    # restore
    p_restore = snap_sub.add_parser("restore", help="Restore a snapshot")
    p_restore.add_argument("name", help="Snapshot name to restore")
    p_restore.set_defaults(func=cmd_snapshot_restore)

    # delete
    p_delete = snap_sub.add_parser("delete", help="Delete a snapshot")
    p_delete.add_argument("name", help="Snapshot name to delete")
    p_delete.set_defaults(func=cmd_snapshot_delete)
