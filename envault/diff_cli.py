"""CLI commands for diffing vault contents."""

import argparse
import sys

from envault.diff import diff_vaults, format_diff
from envault.vault import load_vault
from envault.file_utils import read_dotenv_file


def cmd_diff(args: argparse.Namespace) -> None:
    """Compare the current vault against a .env file or another vault snapshot."""
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("Vault password: ")

    try:
        current = load_vault(password)
    except Exception as exc:
        print(f"Error loading vault: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.file:
        try:
            other = read_dotenv_file(args.file)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No comparison target provided. Use --file <dotenv>.", file=sys.stderr)
        sys.exit(1)

    entries = diff_vaults(
        old=current,
        new=other,
        show_unchanged=args.show_unchanged,
    )
    output = format_diff(entries, mask_values=not args.show_values)
    print(output)


def register_diff_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    diff_parser = subparsers.add_parser(
        "diff",
        help="Diff vault contents against a .env file",
    )
    diff_parser.add_argument(
        "--file", "-f",
        metavar="PATH",
        help="Path to a .env file to compare against",
    )
    diff_parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Also display keys that are identical in both sources",
    )
    diff_parser.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Display actual values instead of masking them",
    )
    diff_parser.add_argument(
        "--password", "-p",
        default=None,
        help="Vault password (prompted if omitted)",
    )
    diff_parser.set_defaults(func=cmd_diff)
