"""CLI commands for copying and renaming vault variables."""

import argparse

from envault.copy import copy_var, rename_var, CopyError
from envault.cli import _get_password


def cmd_copy(args: argparse.Namespace) -> None:
    """Handle the 'copy' subcommand."""
    password = _get_password()
    try:
        copy_var(
            src_key=args.src,
            dst_key=args.dst,
            password=password,
            overwrite=args.overwrite,
        )
        print(f"Copied '{args.src}' -> '{args.dst}'.")
    except CopyError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_rename(args: argparse.Namespace) -> None:
    """Handle the 'rename' subcommand."""
    password = _get_password()
    try:
        rename_var(
            src_key=args.src,
            dst_key=args.dst,
            password=password,
            overwrite=args.overwrite,
        )
        print(f"Renamed '{args.src}' -> '{args.dst}'.")
    except CopyError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def register_copy_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register 'copy' and 'rename' subcommands onto the given subparsers."""
    # copy
    p_copy = subparsers.add_parser("copy", help="Copy a variable to a new key")
    p_copy.add_argument("src", help="Source variable name")
    p_copy.add_argument("dst", help="Destination variable name")
    p_copy.add_argument(
        "--overwrite", action="store_true", help="Overwrite destination if it exists"
    )
    p_copy.set_defaults(func=cmd_copy)

    # rename
    p_rename = subparsers.add_parser("rename", help="Rename a variable")
    p_rename.add_argument("src", help="Current variable name")
    p_rename.add_argument("dst", help="New variable name")
    p_rename.add_argument(
        "--overwrite", action="store_true", help="Overwrite destination if it exists"
    )
    p_rename.set_defaults(func=cmd_rename)
