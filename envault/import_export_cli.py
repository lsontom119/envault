"""CLI commands for importing and exporting vault data as files."""

import argparse
import sys
from pathlib import Path

from envault.cli import _get_password
from envault.vault import load_vault, set_var
from envault.exporter import to_export_script, to_dotenv
from envault.audit import record_event


def cmd_import(args):
    """Import variables from a .env file into the vault."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    password = _get_password(confirm=False)
    imported = 0
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            set_var(key, value, password)
            record_event("import", key)
            imported += 1
    print(f"Imported {imported} variable(s) from '{path}'.")


def cmd_export_file(args):
    """Export vault variables to a file."""
    password = _get_password(confirm=False)
    data = load_vault(password)
    fmt = args.format

    if fmt == "dotenv":
        content = to_dotenv(data)
        default_name = ".env"
    else:
        content = to_export_script(data)
        default_name = "export_vars.sh"

    out_path = Path(args.output) if args.output else Path(default_name)
    out_path.write_text(content)
    record_event("export_file", detail=str(out_path))
    print(f"Exported {len(data)} variable(s) to '{out_path}'.")


def register_import_export_commands(subparsers):
    p_import = subparsers.add_parser("import", help="Import variables from a .env file")
    p_import.add_argument("file", help="Path to .env file")
    p_import.set_defaults(func=cmd_import)

    p_export = subparsers.add_parser("export-file", help="Export variables to a file")
    p_export.add_argument("--format", choices=["dotenv", "shell"], default="dotenv")
    p_export.add_argument("--output", help="Output file path", default=None)
    p_export.set_defaults(func=cmd_export_file)
