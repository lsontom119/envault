"""CLI entry point for envault using argparse."""

import argparse
import sys
from getpass import getpass

from envault.vault import VaultError, get_var, set_var
from envault.exporter import to_export_script, to_dotenv


def cmd_set(args):
    password = getpass("Vault password: ")
    try:
        set_var(args.key, args.value, password)
        print(f"✔ Set {args.key}")
    except VaultError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_get(args):
    password = getpass("Vault password: ")
    try:
        value = get_var(args.key, password)
        if value is None:
            print(f"Key '{args.key}' not found.", file=sys.stderr)
            sys.exit(1)
        print(value)
    except VaultError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export(args):
    password = getpass("Vault password: ")
    try:
        from envault.vault import load_vault
        data = load_vault(password)
        if args.format == "dotenv":
            print(to_dotenv(data))
        else:
            print(to_export_script(data))
    except VaultError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Securely manage and sync environment variables.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Set an environment variable")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Get an environment variable")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_export = sub.add_parser("export", help="Export vault variables")
    p_export.add_argument(
        "--format", choices=["shell", "dotenv"], default="shell"
    )
    p_export.set_defaults(func=cmd_export)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
