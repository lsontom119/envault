"""CLI commands for environment variable health checks."""
from __future__ import annotations

import argparse
import sys

from envault.cli import _get_password
from envault.env_check import EnvCheckError, run_checks


def cmd_check(args: argparse.Namespace) -> None:
    """Run health checks against vault variables."""
    password = _get_password()
    required_keys = args.require or []
    patterns: dict[str, str] = {}
    for spec in args.pattern or []:
        if ":" not in spec:
            print(f"[envault] Invalid pattern spec '{spec}', expected KEY:REGEX", file=sys.stderr)
            sys.exit(1)
        key, _, pattern = spec.partition(":")
        patterns[key.strip()] = pattern.strip()

    if not required_keys and not patterns:
        print("[envault] No checks specified. Use --require or --pattern.", file=sys.stderr)
        sys.exit(1)

    try:
        report = run_checks(password, required_keys=required_keys, patterns=patterns)
    except EnvCheckError as exc:
        print(f"[envault] {exc}", file=sys.stderr)
        sys.exit(1)

    for result in report.results:
        status = "✓" if result.passed else "✗"
        print(f"  {status}  {result.message}")

    if report.ok:
        print(f"\n[envault] All {len(report.results)} check(s) passed.")
    else:
        print(
            f"\n[envault] {len(report.failed)} of {len(report.results)} check(s) failed.",
            file=sys.stderr,
        )
        sys.exit(1)


def register_check_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'check' subcommand."""
    p = subparsers.add_parser("check", help="Run health checks on vault variables")
    p.add_argument(
        "--require",
        metavar="KEY",
        action="append",
        help="Assert that KEY is present and non-empty (repeatable)",
    )
    p.add_argument(
        "--pattern",
        metavar="KEY:REGEX",
        action="append",
        help="Assert that KEY matches REGEX (repeatable)",
    )
    p.set_defaults(func=cmd_check)
