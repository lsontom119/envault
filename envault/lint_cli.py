"""CLI commands for linting vault variables."""

import argparse
import sys

from envault.lint import lint_vault, LintError, Severity
from envault.vault import load_vault, VaultError


def cmd_lint(args: argparse.Namespace) -> int:
    """Run lint checks against the current vault.

    Exits with code 0 if no errors found, 1 if errors exist.
    Warnings do not affect the exit code unless --strict is passed.
    """
    try:
        password = args.password
        vault = load_vault(password)
    except VaultError as exc:
        print(f"[envault] Error loading vault: {exc}", file=sys.stderr)
        return 1

    try:
        result = lint_vault(vault)
    except LintError as exc:
        print(f"[envault] Lint error: {exc}", file=sys.stderr)
        return 1

    if not result.issues:
        print("[envault] No lint issues found.")
        return 0

    # Group issues by severity for display
    errors = result.errors()
    warnings = result.warnings()
    infos = result.infos() if hasattr(result, "infos") else []

    for issue in errors:
        print(f"  ERROR   {issue}")
    for issue in warnings:
        print(f"  WARNING {issue}")
    for issue in infos:
        print(f"  INFO    {issue}")

    total = len(result.issues)
    n_errors = len(errors)
    n_warnings = len(warnings)
    print(
        f"\n[envault] {total} issue(s) found: "
        f"{n_errors} error(s), {n_warnings} warning(s)."
    )

    if n_errors > 0:
        return 1
    if args.strict and n_warnings > 0:
        return 1
    return 0


def cmd_lint_rules(args: argparse.Namespace) -> int:
    """List all available lint rules and their descriptions."""
    from envault.lint import RULES  # imported here to avoid circular deps at module load

    if not RULES:
        print("[envault] No lint rules registered.")
        return 0

    print(f"{'Rule':<30} {'Severity':<10} Description")
    print("-" * 72)
    for rule in RULES:
        severity = getattr(rule, "severity", Severity.WARNING).name
        description = getattr(rule, "description", "No description available.")
        name = getattr(rule, "name", type(rule).__name__)
        print(f"{name:<30} {severity:<10} {description}")
    return 0


def register_lint_commands(
    subparsers: argparse._SubParsersAction,
    password_arg_fn,
) -> None:
    """Register lint-related subcommands onto the provided subparsers.

    Args:
        subparsers: The argparse subparsers action to attach commands to.
        password_arg_fn: A callable that adds the --password argument to a parser.
    """
    # --- lint ---
    lint_parser = subparsers.add_parser(
        "lint",
        help="Check vault variables for common issues.",
    )
    password_arg_fn(lint_parser)
    lint_parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as errors (non-zero exit code).",
    )
    lint_parser.set_defaults(func=cmd_lint)

    # --- lint-rules ---
    rules_parser = subparsers.add_parser(
        "lint-rules",
        help="List all available lint rules.",
    )
    rules_parser.set_defaults(func=cmd_lint_rules)
