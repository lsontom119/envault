"""CLI entry point for envault."""

import argparse
import sys
import os

from envault.vault import load_vault, save_vault, set_var, get_var, VaultError
from envault.exporter import to_export_script, to_dotenv, to_dict
from envault.sync import push_vault, pull_vault, save_remote_config, get_remote_config, SyncError
from envault.remote_config import get_remote_config_path, remote_config_exists


def _get_password(args) -> str:
    return args.password or os.environ.get("ENVAULT_PASSWORD", "")


def cmd_set(args):
    pw = _get_password(args)
    set_var(args.key, args.value, pw)
    print(f"Set {args.key}")


def cmd_get(args):
    pw = _get_password(args)
    try:
        val = get_var(args.key, pw)
        print(val)
    except KeyError:
        print(f"Key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_export(args):
    pw = _get_password(args)
    data = load_vault(pw)
    if args.format == "dotenv":
        print(to_dotenv(data))
    elif args.format == "dict":
        print(to_dict(data))
    else:
        print(to_export_script(data))


def cmd_remote_add(args):
    cfg_path = get_remote_config_path()
    save_remote_config(cfg_path, args.url, args.token)
    print(f"Remote configured: {args.url}")


def cmd_push(args):
    from envault.vault import _get_vault_path
    cfg_path = get_remote_config_path()
    cfg = get_remote_config(cfg_path)
    if not cfg:
        print("No remote configured. Run: envault remote add <url> <token>", file=sys.stderr)
        sys.exit(1)
    try:
        push_vault(_get_vault_path(), cfg["url"], cfg["token"])
        print("Vault pushed to remote.")
    except SyncError as e:
        print(f"Push failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args):
    from envault.vault import _get_vault_path
    cfg_path = get_remote_config_path()
    cfg = get_remote_config(cfg_path)
    if not cfg:
        print("No remote configured. Run: envault remote add <url> <token>", file=sys.stderr)
        sys.exit(1)
    try:
        pull_vault(_get_vault_path(), cfg["url"], cfg["token"])
        print("Vault pulled from remote.")
    except SyncError as e:
        print(f"Pull failed: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envault", description="Manage encrypted env vars")
    parser.add_argument("--password", default=None, help="Vault password")
    sub = parser.add_subparsers(dest="command")

    p_set = sub.add_parser("set", help="Set a variable")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Get a variable")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_exp = sub.add_parser("export", help="Export variables")
    p_exp.add_argument("--format", choices=["shell", "dotenv", "dict"], default="shell")
    p_exp.set_defaults(func=cmd_export)

    p_remote = sub.add_parser("remote", help="Configure remote sync")
    remote_sub = p_remote.add_subparsers(dest="remote_command")
    p_add = remote_sub.add_parser("add", help="Add remote")
    p_add.add_argument("url")
    p_add.add_argument("token")
    p_add.set_defaults(func=cmd_remote_add)

    sub.add_parser("push", help="Push vault to remote").set_defaults(func=cmd_push)
    sub.add_parser("pull", help="Pull vault from remote").set_defaults(func=cmd_pull)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
