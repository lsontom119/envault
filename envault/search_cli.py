"""CLI commands for searching vault variables."""
import argparse
from envault.search import search_vars, SearchError
from envault.cli import _get_password


def cmd_search(args: argparse.Namespace) -> None:
    """Handle the 'search' sub-command."""
    password = _get_password()
    try:
        results = search_vars(
            password,
            args.pattern,
            keys_only=args.keys_only,
        )
    except SearchError as exc:
        print(f"Error: {exc}")
        return

    if not results:
        print("No matches found.")
        return

    for key, value in results.items():
        if args.keys_only:
            print(key)
        else:
            print(f"{key}={value}")


def register_search_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register search-related sub-commands on *subparsers*."""
    p = subparsers.add_parser("search", help="Search vault variables")
    p.add_argument("pattern", help="Substring to search for (case-insensitive)")
    p.add_argument(
        "--keys-only",
        action="store_true",
        default=False,
        help="Only search variable names, not values",
    )
    p.set_defaults(func=cmd_search)
