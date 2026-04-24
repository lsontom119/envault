"""CLI commands for the template-rendering feature."""

import argparse
import sys

from envault.template import TemplateError, list_placeholders, render_file, render_string
from envault.vault import VaultError, load_vault


def cmd_template_render(args: argparse.Namespace) -> None:
    """Render a template file using variables from the vault."""
    try:
        variables = load_vault(args.password)
    except VaultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    strict = not args.ignore_missing

    try:
        rendered = render_file(args.template, variables, strict=strict)
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(rendered)
            print(f"Rendered template written to '{args.output}'.")
        except OSError as exc:
            print(f"error: cannot write output file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(rendered, end="")


def cmd_template_vars(args: argparse.Namespace) -> None:
    """List all placeholder variable names found in a template file."""
    try:
        with open(args.template, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        print(f"error: cannot read template file: {exc}", file=sys.stderr)
        sys.exit(1)

    placeholders = list_placeholders(content)
    if placeholders:
        for name in placeholders:
            print(name)
    else:
        print("No placeholders found.")


def register_template_commands(
    subparsers: argparse._SubParsersAction,
    password_arg_fn,
) -> None:
    """Register 'template render' and 'template vars' sub-commands."""
    p_render = subparsers.add_parser(
        "template-render", help="Render a template file with vault variables"
    )
    password_arg_fn(p_render)
    p_render.add_argument("template", help="Path to the template file")
    p_render.add_argument("-o", "--output", help="Write rendered output to this file")
    p_render.add_argument(
        "--ignore-missing",
        action="store_true",
        default=False,
        help="Leave unknown placeholders unchanged instead of raising an error",
    )
    p_render.set_defaults(func=cmd_template_render)

    p_vars = subparsers.add_parser(
        "template-vars", help="List placeholders used in a template file"
    )
    p_vars.add_argument("template", help="Path to the template file")
    p_vars.set_defaults(func=cmd_template_vars)
