"""CLI commands for vault change history."""

import argparse
from envault.history import get_history, clear_history, HistoryError
from envault.vault import _get_vault_path


def cmd_history_log(args: argparse.Namespace) -> None:
    """Display recent change history for the vault."""
    vault_path = _get_vault_path(args.vault_dir if hasattr(args, "vault_dir") else None)
    try:
        entries = get_history(vault_path, limit=args.limit)
    except HistoryError as exc:
        print(f"Error reading history: {exc}")
        raise SystemExit(1)

    if not entries:
        print("No history recorded yet.")
        return

    for entry in entries:
        key_part = f"  key={entry.key}" if entry.key else ""
        print(f"[{entry.formatted_time()}]  {entry.action:<10}{key_part}")


def cmd_history_clear(args: argparse.Namespace) -> None:
    """Clear the vault change history."""
    vault_path = _get_vault_path(args.vault_dir if hasattr(args, "vault_dir") else None)
    clear_history(vault_path)
    print("History cleared.")


def register_history_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register 'history' subcommands onto an existing subparsers group."""
    history_parser = subparsers.add_parser(
        "history", help="View or clear vault change history"
    )
    history_sub = history_parser.add_subparsers(dest="history_cmd", required=True)

    # history log
    log_parser = history_sub.add_parser("log", help="Show recent changes")
    log_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="Maximum number of entries to show (default: 50)",
    )
    log_parser.set_defaults(func=cmd_history_log)

    # history clear
    clear_parser = history_sub.add_parser("clear", help="Clear change history")
    clear_parser.set_defaults(func=cmd_history_clear)
