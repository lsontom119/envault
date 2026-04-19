"""CLI helpers for audit log commands."""

import json
from typing import Optional

from envault.audit import get_events, clear_events


def cmd_audit_log(args) -> None:
    """Display the audit log."""
    events = get_events()
    if not events:
        print("No audit events recorded.")
        return

    limit: Optional[int] = getattr(args, "limit", None)
    if limit and limit > 0:
        events = events[-limit:]

    fmt: str = getattr(args, "format", "text")
    if fmt == "json":
        print(json.dumps(events, indent=2))
    else:
        for event in events:
            key_part = f"  key={event['key']}" if "key" in event else ""
            print(f"[{event['timestamp']}] {event['action']}{key_part}")


def cmd_audit_clear(args) -> None:
    """Clear the audit log after confirmation."""
    force: bool = getattr(args, "force", False)
    if not force:
        confirm = input("Clear all audit events? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return
    clear_events()
    print("Audit log cleared.")


def register_audit_commands(subparsers) -> None:
    """Register audit subcommands on an argparse subparsers object."""
    audit_parser = subparsers.add_parser("audit", help="Manage audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    log_parser = audit_sub.add_parser("log", help="Show audit events")
    log_parser.add_argument("--limit", type=int, default=0, help="Show last N events")
    log_parser.add_argument("--format", choices=["text", "json"], default="text")
    log_parser.set_defaults(func=cmd_audit_log)

    clear_parser = audit_sub.add_parser("clear", help="Clear audit log")
    clear_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    clear_parser.set_defaults(func=cmd_audit_clear)
