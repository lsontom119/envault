"""CLI commands for variable tag management."""
from __future__ import annotations

import argparse

from envault.cli import _get_password
from envault.tags import TagError, add_tag, list_tags, remove_tag, vars_with_tag


def cmd_tag_add(args: argparse.Namespace) -> None:
    password = _get_password()
    try:
        add_tag(password, args.name, args.tag)
        print(f"Tag '{args.tag}' added to '{args.name}'.")
    except TagError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_tag_remove(args: argparse.Namespace) -> None:
    password = _get_password()
    try:
        remove_tag(password, args.name, args.tag)
        print(f"Tag '{args.tag}' removed from '{args.name}'.")
    except TagError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_tag_list(args: argparse.Namespace) -> None:
    password = _get_password()
    var_name = getattr(args, "name", None)
    tags = list_tags(password, var_name=var_name)
    if not tags:
        print("No tags found.")
        return
    for var, tag_list in sorted(tags.items()):
        print(f"{var}: {', '.join(sorted(tag_list))}")


def cmd_tag_vars(args: argparse.Namespace) -> None:
    password = _get_password()
    matches = vars_with_tag(password, args.tag)
    if not matches:
        print(f"No variables tagged with '{args.tag}'.")
        return
    for name in sorted(matches):
        print(name)


def register_tag_commands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    tag_parser = subparsers.add_parser("tag", help="Manage variable tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_command", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a variable")
    p_add.add_argument("name", help="Variable name")
    p_add.add_argument("tag", help="Tag to add")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a variable")
    p_rm.add_argument("name", help="Variable name")
    p_rm.add_argument("tag", help="Tag to remove")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_list = tag_sub.add_parser("list", help="List tags")
    p_list.add_argument("name", nargs="?", default=None, help="Variable name (omit for all)")
    p_list.set_defaults(func=cmd_tag_list)

    p_vars = tag_sub.add_parser("vars", help="List variables with a given tag")
    p_vars.add_argument("tag", help="Tag to filter by")
    p_vars.set_defaults(func=cmd_tag_vars)
